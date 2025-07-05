from flask import Blueprint, jsonify, request
import MySQLdb.cursors

units_bp = Blueprint('units', __name__, url_prefix='/units')

mysql = None
bcrypt = None

def init_app(app, _mysql):
    global mysql, bcrypt
    mysql = _mysql


@units_bp.route('/',methods=['GET'])
def get_all_units():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM master_unit")
    rows = cursor.fetchall()
    return jsonify({"units" : rows})