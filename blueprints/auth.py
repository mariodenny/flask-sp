from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
import MySQLdb.cursors

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

mysql = None
bcrypt = None

def init_app(app, _mysql, _bcrypt):
    global mysql, bcrypt
    mysql = _mysql
    bcrypt = _bcrypt

@auth_bp.route('/login', methods=["POST"])
def login():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    nik = request.json['nik']
    password = request.json['password']

    cursor.execute("SELECT * FROM users WHERE nik = %s", (nik,))
    user = cursor.fetchone()

    if user:
        hashed_password = user['password']
        if bcrypt.check_password_hash(hashed_password, password):
            return jsonify({
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "email": user.get('email', None),
                    "nik" : user.get('nik'),
                    "role" : user.get('role')
                }
            })
        else:
            return jsonify({"error": "Password mismatch"}), 401
    else:
        return jsonify({"error": "User not found"}), 404

@auth_bp.route('/user', methods=['POST'])
def add_user():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        data = request.get_json()
        print(f"Data {data}")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role") 
        m_department_id = data.get("m_department_id")
        nik = data.get("nik")

        # Validasi wajib isi
        if not all([username, email, password, role, m_department_id, nik]):
            return jsonify({"error": "All fields are required!"}), 400

        # Cek duplikat username
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "Username already registered!"}), 400

        # Cek duplikat email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already registered!"}), 400

        # Cek duplikat nik
        cursor.execute("SELECT id FROM users WHERE nik = %s", (nik,))
        if cursor.fetchone():
            return jsonify({"error": "NIK already registered!"}), 400

        hash_password = bcrypt.generate_password_hash(password)
        # Jika semua aman -> insert user baru
        cursor.execute("""
            INSERT INTO users (username, email, password, role, m_department_id, nik)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, email, hash_password, role, m_department_id, nik))

        mysql.connection.commit()

        return jsonify({"success": "User added successfully!"}), 201

    except Exception as e:
        print(f"Error adding user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        cursor.close()

@auth_bp.route('/user', methods=['PUT'])
def update_user():
    pass
