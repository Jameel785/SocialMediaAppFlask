from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# this will convert the file into a web application
app = Flask(__name__)
app.config['SECRET_KEY'] = '15fe26a73acd9ed948d11ca07f2b50aa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from schoolgram import routes