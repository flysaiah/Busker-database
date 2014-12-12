# This is the main file that is declared in the Procfile as our app
from flask import Flask, render_template, redirect, url_for, flash
from forms import SignupForm, LoginForm, PerformerSignupForm, ConcertForm, ConcertSearchForm, PerformerSearchForm
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from flask.ext.sqlalchemy import *
from flask.ext.security import login_required



app = Flask(__name__)
app.debug = True
app.config.from_object('config')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buskerdb.db'
db = SQLAlchemy(app)



















