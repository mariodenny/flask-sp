from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from blueprints.auth import auth_bp, init_app as init_auth
from blueprints.dashboard import dashboard_bp, init_app as init_dashboard
from blueprints.units import units_bp, init_app as init_units
from blueprints.category import category_bp , init_app as init_category
from blueprints.product import product_bp , init_app as init_product
from blueprints.department import department_bp, init_app as init_department

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Initialize blueprints with dependencies
init_auth(app, mysql, bcrypt)
init_dashboard(app,mysql)
init_units(app,mysql)
init_category(app,mysql)
init_product(app,mysql)
init_department(app,mysql)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(units_bp)
app.register_blueprint(category_bp)
app.register_blueprint(product_bp)
app.register_blueprint(department_bp)

if __name__ == '__main__':
    app.run(debug=True)
