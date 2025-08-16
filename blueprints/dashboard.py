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
    u.username,
    d.`name` AS department_name,
    p.`name` AS product_name,
    t.transaction_date,
    t.transaction_type,
    t.`description`,
    t.qty AS transaction_qty,
    s.qty AS stock_qty,
    SUM(CASE 
        WHEN t.transaction_type = 'IN' THEN t.qty
        WHEN t.transaction_type = 'OUT' THEN -t.qty
        ELSE 0 END
    ) OVER (PARTITION BY t.m_product_id ORDER BY t.transaction_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS balance
FROM transactions t
INNER JOIN master_products p ON t.m_product_id = p.id
INNER JOIN users u ON t.created_by = u.id
INNER JOIN master_departments d ON u.m_department_id = d.id
INNER JOIN stocks s ON t.m_product_id = s.m_product_id;

    """)

    rows = cursor.fetchall()
    return jsonify({"transactions" : rows})
