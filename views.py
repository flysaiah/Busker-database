from flask import Flask, render_template, redirect, url_for, flash
from forms import SignupForm, LoginForm, PerformerSignupForm, ConcertForm, ConcertSearchForm, PerformerSearchForm
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from flask.ext.security import login_required
from app import app
from model import db, User, Performer, Concert


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

@app.route('/deleteaccount', methods=['GET', 'POST'])
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
	return render_template('login.html', form=form, delete=True)

@app.route('/favorites')
@login_required
def displayfavorites():
	user = current_user._get_current_object()
	if user.isPerformer():
		flash("Performers do not have a list of favorites")
		return redirect(url_for('frontpage'))
	favorite_performers = user.favorites
	return render_template('favorites.html', favorite_performers=favorite_performers)

@app.route('/followers')
@login_required
def displayfollowers():
	performer = current_user._get_current_object()
	if not performer.isPerformer():
		flash("Users do not have followers")
		return redirect(url_for('frontpage'))
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
		return redirect('/favorites')

@app.route('/search/performer', methods=['GET', 'POST'])
def searchperformer():
	form = PerformerSearchForm()
	if form.validate_on_submit():
		performer = Performer.query.filter_by(name=form.performername.data).first()
		return render_template('performerpage.html', performer=performer)
	return render_template('performersearch.html')

@app.route('/upcoming-concerts')
@login_required
def displayupcomingconcerts():
	currentuser = current_user._get_current_object()
	if currentuser.isPerformer():
		flash("Performers cannot view this page")
		return redirect(url_for('frontpage'))
	concerts = currentuser.followed_concerts()
	return render_template('concerts.html', concerts=concerts)

@app.route('/all-concerts')
def displayallconcerts():
	concerts = []
	for performer in Performer.query.all():
		for performance in performer.performances:
			concerts.append(performance)
	return render_template('concerts.html', concerts=concerts)

@app.route('/special/easteregg')
def specialfunction():
	return render_template('easteregg.html')

@app.route('/search/concerts', methods=['GET', 'POST'])
def searchconcerts():
	form = ConcertSearchForm()
	if form.validate_on_submit():  #Will convert this into a controller function
		foundperformances = []
		if form.byperformer.data is not None:
			performer = Performer.query.filter_by(name=form.byperformer.data).first()
			for performance in performer.performances:
				foundperformances.append(performance)
		else:
			foundperformances = Concert.query.all()

		if form.bystreetaddress.data is not None:
			for performance in foundperformances:
				if performance.streetaddress != form.streetaddress.data:
					foundperformances.remove(performance)
		if form.bycity.data is not None:
			for performance in foundperformances:
				if performance.city != form.bycity.data:
					foundperformances.remove(performance)
		if form.bystate.data is not None:
			for performance in foundperformances:
				if performance.state != form.bystate.data:
					foundperformances.remove(performance)
		concerts = foundperformances
		return render_template('concerts.html', concerts=concerts)
	return render_template('searchconcerts.html')

@app.route('/createconcert', methods=['GET', 'POST'])
@login_required
def createconcert():
	if not current_user._get_current_object().isPerformer():
		flash("Non-performers cannot create concerts")
		return redirect(url_for('frontpage'))
	form = ConcertForm()
	if form.validate_on_submit():
		newconcert = Concert(form.time.data, form.streetaddress.data, form.city.data, form.state.data, current_user._get_current_object().performer_email)
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

@app.route('/concerts/<performeremail>')
def concertsbyperformer(performeremail):
	performer = Performer.query.filter_by(performer_email=performeremail).first()
	concerts = performer.performances
	return render_template('concerts.html', concerts=concerts)

@app.route('/edit/concert/<concert_id>', methods=['GET', 'POST'])
@login_required
def editconcert(concert_id):
	if not current_user._get_current_object().isPerformer():
		flash("Non-performers cannot edit concerts")
		return redirect(url_for('frontpage'))
	concert = Concert.query.get_or_404(concert_id)
	form = ConcertForm()
	form.time.data = concert.time
	form.streetaddress.data = concert.streetaddress
	performerstring = ""
	for performer in concert.performers:
		performerstring = performerstring + performer.name + ","
	performerstring = performerstring[:-1]
	form.addperformers.data = performerstring
	if form.validate_on_submit():
		db.session.delete(concert)
		db.session.commit()
		newconcert = Concert(form.time.data, form.streetaddress.data, form.city.data, form.state.data, current_user._get_current_object().performer_email)
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
		flash("Concert edited successfully")
		return redirect(url_for('frontpage'))
	return render_template('editconcert.html', form=form)

@app.route('/deleteconcert/<concert_id>')
@login_required
def deleteconcert(concert_id):
	currentuser = current_user._get_current_object()
	performeremail = currentuser.performer_email
	if not currentuser.isPerformer():
		flash("Non-performers cannot delete concerts.")
		return redirect(url_for('frontpage'))
	concert = Concert.query.get_or_404(concert_id)
	if performeremail != concert.owner:
		flash("You are not the owner of this concert")
		return redirect(url_for('concerts', performeremail=performeremail))
	else:
		db.session.delete(concert)
		db.session.commit()
		flash("Concert successfully deleted")
		return redirect(url_for('concerts', performeremail=performeremail))
	