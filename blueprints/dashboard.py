from flask import Blueprint, jsonify, request
import MySQLdb.cursors

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

mysql = None
bcrypt = None

def init_app(app, _mysql):
    global mysql, bcrypt
    mysql = _mysql



@dashboard_bp.route('/', methods=["GET"])
def get_stock():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
   SELECT 
    users.username,
    master_departments.`name` AS department_name,
    master_products.`name` AS product_name,
    transactions.transaction_date,
    transactions.transaction_type,
    transactions.`description`,
    transactions.qty AS transaction_qty,
    stocks.qty AS stock_qty,
    CASE 
        WHEN transactions.transaction_type = 'IN' THEN transactions.qty + stocks.qty
        WHEN transactions.transaction_type = 'OUT' THEN stocks.qty - transactions.qty
		  ELSE stocks.qty
   		
    END AS balance
FROM transactions
INNER JOIN master_products ON transactions.m_product_id = master_products.id
INNER JOIN users ON transactions.created_by = users.id
INNER JOIN master_departments ON users.m_department_id = master_departments.id
INNER JOIN stocks ON transactions.m_product_id = stocks.m_product_id;

    """)

    rows = cursor.fetchall()
    return jsonify({"transactions" : rows})
