from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from blueprints.auth import auth_bp, init_app as init_auth
from blueprints.dashboard import dashboard_bp, init_app as init_dashboard
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

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True)
