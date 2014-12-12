from flask import Flask
from flask.ext.sqlalchemy import *

app = Flask(__name__)
app.debug = True
app.config.from_object('config')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buskerdb.db'
db = SQLAlchemy(app)

import views
