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

performances = db.Table('performances', db.Column('email_of_performer', db.Text, db.ForeignKey('performer.performer_email')), db.Column('concert_id', db.Integer, db.ForeignKey('concert.generated_id')))
favorites = db.Table('favorites', db.Column('p_email', db.Text, db.ForeignKey('performer.performer_email')), db.Column('u_email', db.Text, db.ForeignKey('user.user_email')))
attendings = db.Table('attendings', db.Column('email_of_user', db.Text, db.ForeignKey('user.user_email')), db.Column('id_of_concert', db.Integer, db.ForeignKey('concert.generated_id')))

class Performer(db.Model):
	performer_email = db.Column(db.Text, primary_key=True)
	name = db.Column(db.Text)
	performer_password = db.Column(db.Text)
	performances = db.relationship('Concert', secondary=performances, backref=db.backref('performers', lazy='dynamic'), lazy='dynamic')

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
	def isPerformer():
		return True

class User(db.Model):
	user_email = db.Column(db.Text, primary_key=True)
	user_password = db.Column(db.Text)
	favorites = db.relationship('Performer', secondary=favorites, backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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
	def favorite(self, performer):
		if not self.has_favorited(performer):
			self.favorites.append(performer)
			return self
	def unfavorite(self, performer):
		if self.has_favorited(performer):
			self.favorites.remove(performer)
			return self
	def has_favorited(self, performer):
		return self.favorites.filter(favorites.c.p_email == performer.performer_email).count() > 0
	def followed_concerts(self):
		return Concert.query.join(favorites, (favorites.c.p_email == Performer.performer_email)).filter(favorites.c.u_email == self.user_email)
	def isPerformer():
		return False

class Concert(db.Model):
	generated_id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Text)
	place = db.Column(db.Text)
	owner = db.Column(db.Text)
	attendees = db.relationship('User', secondary=attendings, backref=db.backref('concerts', lazy='dynamic'), lazy='dynamic')

	def __init__(self, time, place, owner):
		self.time = time
		self.place = place
		self.owner = owner
	def __repr__(self):
		return '<Concert at {0}, {1}>'.format(self.place, self.time)
	def addPerformer(self, performer):
		self.performers.append(performer)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(useremail):
	if User.query.get(useremail) is None:
		return Performer.query.get(useremail)
	else:
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
			login_user(performer)
		else:
			user = User.query.get_or_404(form.email_username.data)
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

@app.route('/deleteaccount')
@login_required
def confirmdeletion():
	form = LoginForm()
	if form.validate_on_submit():
		currentuser = current_user._get_current_object()
		logout_user()
		db.session.delete(currentuser)
		db.session.commit()
		flash("Account deletion successful")
		return redirect(url_for('frontpage'))
	return render_template('confirmdeletion.html', form=form)

@app.route('/favorites')
@login_required
def displayfavorites():
	user = current_user._get_current_object()
	favorite_performers = user.favorites
	return render_template('favorites.html', favorite_performers=favorite_performers)

@app.route('/followers')
@login_required
def displayfollowers():
	performer = current_user._get_current_object()
	followers = performer.followers
	return render_template('followers.html', followers=followers)

@app.route('/favorite/<performer_email>')
@login_required
def followperformer(performer_email):
	performer = Performer.query.get_or_404(performer_email)
	user = current_user._get_current_object()
	if user.isPerformer():
		flash("Performers cannot favorite/unfavorite other performers; please create a user account")
		return redirect(url_for('frontpage'))
	else:
		favorite_object = user.favorite(performer)
		db.session.add(favorite_object)
		db.session.commit()
		flash("Successfully favorited " + str(performer.name))
		return redirect(url_for('frontpage')) #Eventually will redirect to wherever the favoriting page is

@app.route('/unfavorite/<performer_email>')
@login_required
def unfollowperformer(performer_email):
	performer = Performer.query.get_or_404(performer_email)
	user = current_user._get_current_object()
	if user.isPerformer():
		flash("Performers cannot favorite/unfavorite")
		return redirect(url_for('frontpage'))
	else:
		unfavorite_object = user.unfavorite(performer)
		db.session.add(unfavorite_object)
		db.session.commit()
		flash("Successfully unfavorited " + str(performer.name))
		return redirect(url_for('favorites'))

@app.route('/search/performer')
def searchperformer():
	form = PerformerSearchForm()
	if form.validate_on_submit():
		performer = Performer.query.filter_by(name=form.performername.data).first()
		return render_template('performerpage.html', performer=performer)
	return render_template('performersearch.html')



@app.route('/search/concerts')
def searchconcerts():
	form = ConcertSearchForm()
	if form.validate_on_submit():
		if form.byperformer.data is not None:
			'''if form.bylocation.data is not None:
				performer = Performer.query.filter_by(name=form.byperformer.data).first()
				concerts = performer.performances
				for performance in concerts:''' #Will finish once I figure out location
			#else:
			performer = Performer.query.filter_by(name=form.byperformer.data).first()
			concerts = performer.performances
			return render_template('concerts.html', concerts=concerts)
		#else:
			#Just location stuff
	return render_template('searchconcerts.html')

@app.route('/createconcert')
@login_required
def createconcert():
	form = ConcertForm()
	if form.validate_on_submit():
		newconcert = Concert(form.time.data, form.place.data, current_user._get_current_object().performer_email)
		db.session.add(newconcert)
		db.session.commit()
		performers = []
		performers.append(currentuser._get_current_object())
		if form.addperformers.data is not None:
			names = form.addperformers.data
			names = names.replace(" ", "").split(",")
			for name in names:
				newperformer = Performer.query.get_or_404(name)
				performers.append(newperformer)
		for performer in performers:
			db.session.add(newconcert.addPerformer())
			db.session.commit()
		flash("Concert created successfully")
		return redirect(url_for('frontpage'))
	return render_template('createconcert.html', form=form)













