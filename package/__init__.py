from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
Session(app)

from package import routes, models