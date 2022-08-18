import pdb

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from reviewer import routes, models
import os

app = Flask(__name__)
basedir = os.getcwd()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "Database.db"
)
print(app.config["SQLALCHEMY_DATABASE_URI"])
print('PIPKA')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = "hard to guess"
db = SQLAlchemy(app)
from api import routes, models