from flask import Blueprint, jsonify, request
import MySQLdb.cursors
from datetime import datetime
import pytz

product_bp = Blueprint('products', __name__, url_prefix='/products')

mysql = None
bcrypt = None

def init_app(app, _mysql):
    global mysql, bcrypt
    mysql = _mysql


@product_bp.route('/', methods=['POST'])
def store_product():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        m_category_id = data.get('m_category_id')
        m_unit_id = data.get('m_unit_id')

        if not all([name, description, m_category_id, m_unit_id]):
            return jsonify({"error": "Missing required fields."}), 400
        
        cursor.execute("INSERT INTO master_products (name, description, m_category_id, m_unit_id) VALUES (%s, %s, %s, %s)",
                       (name, description, m_category_id, m_unit_id))
        mysql.connection.commit()

        return jsonify({"success": "New product has been added!"}), 201  
    except Exception as e:
        print(f"Error while storing product: {str(e)}")
        return jsonify({"error": f"Failed to store new product. {str(e)}"}), 500 
    finally:
        cursor.close()

@product_bp.route('/', methods=['GET'])
def get_all_products():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM master_products")
        products = cursor.fetchall()

        return jsonify({"products" : products})

    except Exception as err:
        print(f"Error while storing product: {str(err)}")
        return jsonify({"error": f"Failed to get all products. {str(err)}"}), 500 
    finally:
        cursor.close()

@product_bp.route('/input', methods=['POST'])
def stock_in_product():
    cursor = None
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        data = request.get_json()
        user_id = data.get('user_id')
        m_product_id = data.get('m_product_id')
        description = data.get('description')
        transaction_type = 'IN'  
        qty = data.get('qty')    
        price = data.get('price')
        created_by = user_id   
        transaction_date = datetime.now(pytz.timezone('Asia/Jakarta'))
        created_at = datetime.now(pytz.timezone('Asia/Jakarta'))
        
        total_price = qty * price

        # Step 1: Insert ke transactions
        insert_transaction = """
            INSERT INTO transactions (
                user_id, m_product_id, description, transaction_type, qty,
                transaction_date, created_at, created_by, price, total_price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_transaction, (
            user_id, m_product_id, description, transaction_type, qty,
            transaction_date, created_at, created_by, price, total_price
        ))

        # Step 2: Update stock
        # Cek apakah produk sudah ada di tabel stock
        cursor.execute("SELECT qty, total_price FROM stocks WHERE m_product_id = %s", (m_product_id,))
        existing_stock = cursor.fetchone()

        if existing_stock:
            # Update qty dan total_price
            new_qty = existing_stock['qty'] + qty
            new_total_price = existing_stock['total_price'] + total_price
            new_avg_price = new_total_price / new_qty

            cursor.execute("""
                UPDATE stocks SET qty = %s, price = %s, total_price = %s
                WHERE m_product_id = %s
            """, (new_qty, new_avg_price, new_total_price, m_product_id))
        else:
            # Insert baru ke stock
            cursor.execute("""
                INSERT INTO stocks (m_product_id, qty, price, total_price)
                VALUES (%s, %s, %s, %s)
            """, (m_product_id, qty, price, total_price))

        mysql.connection.commit()
        return jsonify({"message": "Stock successfully added"}), 200

    except MySQLdb.Error as db_err:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Database error: {db_err}")
        return jsonify({"error": f"Database error: {str(db_err)}"}), 500

    except Exception as err:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Unexpected error: {err}")
        return jsonify({"error": f"Failed to process stock operation: {str(err)}"}), 500

    finally:
        if cursor:
            cursor.close()

@product_bp.route('/output', methods=['POST'])
def stock_out_product():
    cursor = None
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        data = request.get_json()
        user_id = data.get('user_id')
        m_product_id = data.get('m_product_id')
        description = data.get('description')  # atau 'description' sesuai payload kamu
        transaction_type = 'OUT'
        qty_out = data.get('qty')

        transaction_date = datetime.now(pytz.timezone('Asia/Jakarta'))
        created_at = transaction_date
        created_by = user_id

        # Ambil stok produk
        cursor.execute("SELECT qty, total_price FROM stocks WHERE m_product_id = %s", (m_product_id,))
        stock = cursor.fetchone()

        if not stock:
            return jsonify({"error": "Produk tidak ditemukan di stok"}), 404

        if stock['qty'] < qty_out:
            return jsonify({"error": "Stok tidak mencukupi"}), 400

        # Hitung rata-rata harga
        avg_price = stock['total_price'] / stock['qty']
        total_price_out = avg_price * qty_out

        # Kurangi stok
        new_qty = stock['qty'] - qty_out
        new_total_price = stock['total_price'] - total_price_out

        cursor.execute("""
            UPDATE stocks SET qty = %s, price = %s, total_price = %s
            WHERE m_product_id = %s
        """, (new_qty, avg_price, new_total_price, m_product_id))

        # Simpan transaksi keluar
        insert_transaction = """
            INSERT INTO transactions (
                user_id, m_product_id, description, transaction_type, qty,
                transaction_date, created_at, created_by, price, total_price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_transaction, (
            user_id, m_product_id, description, transaction_type, qty_out,
            transaction_date, created_at, created_by, avg_price, total_price_out
        ))

        mysql.connection.commit()
        return jsonify({"message": "Stock successfully removed"}), 200

    except MySQLdb.Error as db_err:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Database error: {db_err}")
        return jsonify({"error": f"Database error: {str(db_err)}"}), 500

    except Exception as err:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Unexpected error: {err}")
        return jsonify({"error": f"Failed to process stock operation: {str(err)}"}), 500

    finally:
        if cursor:
            cursor.close()