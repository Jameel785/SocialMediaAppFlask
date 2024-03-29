from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# this will convert the file into a web application
app = Flask(__name__)
app.jinja_env.globals.update(len=len)
app.config['SECRET_KEY'] = '15fe26a73acd9ed948d11ca07f2b50aa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from schoolgram import routes