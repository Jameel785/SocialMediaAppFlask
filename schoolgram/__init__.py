from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# this will convert the file into a web application
app = Flask(__name__)
app.config['SECRET_KEY'] = '15fe26a73acd9ed948d11ca07f2b50aa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from schoolgram import routes