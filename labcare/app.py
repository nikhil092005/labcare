from flask import Flask
from flask_mysqldb import MySQL
from auth import auth_bp, init_app as auth_init
from issues import issues_bp, init_app as issues_init
from ai_chat import ai_chat_bp, init_app as ai_chat_init

app = Flask(__name__)
app.secret_key = 'nikhil092005'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'         # or your MySQL server address
app.config['MYSQL_USER'] = 'root'   # replace with your MySQL username
app.config['MYSQL_PASSWORD'] = '' # replace with your MySQL password
app.config['MYSQL_DB'] = 'labmentor'            # your database name

mysql = MySQL(app)

# Initialize auth module with mysql instance
auth_init(mysql)
issues_init(mysql)
ai_chat_init()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(issues_bp)
app.register_blueprint(ai_chat_bp)

if __name__ == '__main__':
    app.run(debug=True)