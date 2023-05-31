from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd0cb7a1b6870dee8c216133fe5c00c12'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar'
login_manager.login_message_category = 'alert-info'


from blog import routes