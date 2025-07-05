from flask import Blueprint, jsonify, request
import MySQLdb.cursors

category_bp = Blueprint('category', __name__, url_prefix='/category')

mysql = None
bcrypt = None

def init_app(app, _mysql):
    global mysql, bcrypt
    mysql = _mysql


@category_bp.route('/',methods=['GET'])
def get_all_category():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM master_categories")
    rows = cursor.fetchall()
    return jsonify({"category" : rows})