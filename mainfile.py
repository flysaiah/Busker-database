# This is the main file that is declared in the Procfile as our app
from flask import Flask, render_template
from forms import SignupForm, LoginForm

app = Flask(__name__)
app.debug = True
app.config.from_object('config')
