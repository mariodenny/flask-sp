from flask import Blueprint, jsonify, request
import MySQLdb.cursors

department_bp = Blueprint('departments', __name__, url_prefix='/departments')

mysql = None
bcrypt = None

def init_app(app, _mysql):
    global mysql, bcrypt
    mysql = _mysql


@department_bp.route('/',methods=['GET'])
def get_all_departments():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM master_departments")
    rows = cursor.fetchall()
    return jsonify({"departmens" : rows})