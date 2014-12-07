# This is the main file that is declared in the Procfile as our app
from flask import Flask, render_template
from forms import SignupForm, LoginForm

app = Flask(__name__)
app.debug = True
app.config.from_object('config')

@app.route('/')
def frontpage():
	return render_template('frontpage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	#if form.validate_on_submit():
		#do something
	return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	#if form.validate_on_submit():
		#do something
	return render_template('signup.html', form=form)

@app.route('/signup/confirmed')
def signupConfirmed():
	return render_template('frontpage.html')
