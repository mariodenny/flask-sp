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
