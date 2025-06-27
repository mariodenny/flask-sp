from flask import Flask,json,jsonify,request
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors

# Config Mysql
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

mysql = MySQL(app)
bcrypt = Bcrypt(app)


@app.route('/siswa',methods=['GET'])
def get_siswa():
    data = {
        'name' : 'Ujang Suganda',
        'class' : '2A',
        'Mapel' : 'IPA'
    }

    return jsonify(data)
# Methods
@app.route('/post', methods=['GET'])
def get_posts():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM posts" 
    )

    post = cursor.fetchall()
    return jsonify({"post":post})


@app.route('/post/store',methods=['POST'])
def store_post():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # terima passing dari depan
    title = request.form['title_post']
    description = request.form['description']
    user_id = request.form['user_id']

    insert = cursor.execute(
        'INSERT INTO posts(title,description,user_id) VALUE (%s,%s,%s)',
        (title,description, user_id)
    )
    mysql.connection.commit() # commit ->

    if insert:
        return jsonify({"Success" : "Post has been added"})
    else:
        print("Failed")
        return jsonify({"Error" : insert})
    
# Todo fix query search
@app.route('/post/<string:q>') # Search
def get_username(q):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = cursor.execute(f"SELECT * FROM posts WHERE title LIKE %{q}%")
    # print(f"Query : {query}"
    search_param = f"%{q}%"
    cursor.execute(query)
    rows = cursor.fetchall()

    return jsonify({"post" : rows}) 


@app.route('/post/<int:id>')
def get_one_post(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM posts where id=%s',(id,))

    post = cursor.fetchone()
    return jsonify({"post" : post})

@app.route('/post/<int:id>/update', methods=['POST'])
def update_post(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    title_update = request.form['title']
    description_update = request.form['description']
    cursor.execute('UPDATE posts SET title=%s , description=%s where id=%s', (title_update,description_update,id,))
    mysql.connection.commit() # Commit
    return jsonify({'message' : 'Success'})    

@app.route('/post/<int:id>/delete', methods=['DELETE'])
def delete_post(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM posts where id=%s', (id,))
    mysql.connection.commit()

    return jsonify({'message' : 'Success'})    

@app.route('/login', methods=["POST"])
def login():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    username = request.json['username']
    password = request.json['password']

    # Ambil data user
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        hashed_password = user['password']
        if bcrypt.check_password_hash(hashed_password, password):
            return jsonify({
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "email": user.get('email', None)  # kalau ada email
                }
            })
        else:
            return jsonify({"error": "Password mismatch"}), 401
    else:
        return jsonify({"error": "User not found"}), 404