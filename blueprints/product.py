from flask import Blueprint, jsonify, request
import MySQLdb.cursors

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