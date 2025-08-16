from flask import Blueprint, jsonify, request, send_file
import MySQLdb.cursors
import pandas as pd
from io import BytesIO

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

mysql = None

def init_app(app, _mysql):
    global mysql
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
    return jsonify({"transactions": rows})


@dashboard_bp.route('/report', methods=['GET'])
def get_report():
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    file_type = request.args.get("type", "xlsx")  # bisa pilih csv / xlsx

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
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
INNER JOIN stocks s ON t.m_product_id = s.m_product_id
WHERE t.transaction_date BETWEEN %s AND %s
ORDER BY t.transaction_date ASC
"""
    cursor.execute(query, (date_from, date_to))
    rows = cursor.fetchall()

    df = pd.DataFrame(rows)

    # simpan file ke memory
    output = BytesIO()
    if file_type == "csv":
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype="text/csv", as_attachment=True, download_name="report.csv")
    else:
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        output.seek(0)
        return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="report.xlsx")
