# This is the main file that is declared in the Procfile as our app
from flask import Flask, render_template, redirect, url_for
from forms import SignupForm, LoginForm, PerformerSignupForm
from flask.ext.login import LoginManager, login_user, logout_user
from flask.ext.sqlalchemy import *
from flask.ext.security import login_required



app = Flask(__name__)
app.debug = True
app.config.from_object('config')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buskerdb.db'
db = SQLAlchemy(app)

performances = db.Table('performances', db.Column('email_of_performer', db.Text, db.ForeignKey('performer.performer_email')), db.Column('concert_id', db.Integer, db.ForeignKey('concert.generated_id')))
favorites = db.Table('favorites', db.Column('p_email', db.Text, db.ForeignKey('performer.performer_email')), db.Column('u_email', db.Text, db.ForeignKey('user.user_email')))
attendings = db.Table('attendings', db.Column('email_of_user', db.Text, db.ForeignKey('user.user_email')), db.Column('id_of_concert', db.Integer, db.ForeignKey('concert.generated_id')))

class Performer(db.Model):
	performer_email = db.Column(db.Text, primary_key=True)
	name = db.Column(db.Text)
	performer_password = db.Column(db.Text)
	performances = db.relationship('Concert', secondary=performances, backref='performers')

	def __init__(self, performer_email, name, performer_password):
		self.performer_email = performer_email
		self.name = name
		self.performer_password = performer_password
	
	def __repr__(self):
		return '<Performer {0}>'.format(self.performer_email)
	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		try:
			return unicode(self.performer_email)
		except NameError:
			return str(self.performer_email)



class User(db.Model):
	user_email = db.Column(db.Text, primary_key=True)
	user_password = db.Column(db.Text)
	favorites = db.relationship('Performer', secondary=favorites, backref='followers')

	def __init__(self, user_email, user_password):
		self.user_email = user_email
		self.user_password = user_password
	def __repr__(self):
		return '<User {0}>'.format(self.user_email)
	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		try:
			return unicode(self.user_email)
		except NameError:
			return str(self.user_email)

class Concert(db.Model):
	generated_id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Text)
	place = db.Column(db.Text)
	owner = db.Column(db.Text)
	attendees = db.relationship('User', secondary=attendings, backref='concerts')

	def __init__(self, time, place, owner):
		self.time = time
		self.place = place
		self.owner = owner
	def __repr__(self):
		return '<Concert at {0}, {1}>'.format(self.place, self.time)



login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(useremail):
	return User.query.get(useremail)

@app.route('/')
def frontpage():
	return render_template('frontpage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.performer_option.data:
			performer = Performer.query.get_or_404(form.email_username.data)
			if form.password.data == performer.performer_password:
				login_user(performer)
		else:
			user = User.query.get_or_404(form.email_username.data)
			if form.password.data == user.user_password:
				login_user(user)
		return render_template('frontpage.html')
	return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	if form.validate_on_submit():
		newuser = User(form.new_email_username.data, form.new_password.data)
		db.session.add(newuser)
		db.session.commit()
		login_user(newuser)
		return render_template('frontpage.html')
	return render_template('signup.html', form=form)

@app.route('/signup/performer', methods=['GET', 'POST'])
def psignup():
	form = PerformerSignupForm()
	if form.validate_on_submit():
		newperformer = Performer(form.new_email_username.data, form.performer_name.data, form.new_password.data)
		db.session.add(newperformer)
		db.session.commit()
		login_user(newperformer)
		return render_template('frontpage.html')
	return render_template('signup.html', form=form)

@app.route('/signup/confirmed')
def signupConfirmed():
	return redirect(url_for('frontpage'))

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('frontpage'))
