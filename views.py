from flask import Flask, render_template, redirect, url_for, flash
from forms import SignupForm, LoginForm, PerformerSignupForm, ConcertForm, ConcertSearchForm, PerformerSearchForm
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from flask.ext.security import login_required
from app import app
from model import db, User, Performer, Concert
from datetime import date


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

@app.route('/about')
def about():
	return render_template('about.html')

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
		currentuser.active = False
		db.session.commit()
		logout_user()
		flash("Account deletion successful")
		return redirect(url_for('frontpage'))
	return render_template('login.html', form=form, delete=True)

@app.route('/test')
def test():
	currentuser = current_user._get_current_object()
	return render_template('test.html', currentuser=currentuser)

@app.route('/favorites')
@login_required
def displayfavorites():
	user = current_user._get_current_object()
	if user.isPerformer():
		flash("Performers do not have a list of favorites")
		return redirect(url_for('frontpage'))
	favorite_performers = user.favorites.all()
	return render_template('favorites.html', favorite_performers=favorite_performers)

@app.route('/followers')
@login_required
def displayfollowers():
	performer = current_user._get_current_object()
	if not performer.isPerformer():
		flash("Users do not have followers")
		return redirect(url_for('frontpage'))
	followers = performer.followers.all()
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
		if favorite_object is None:
			flash("You are already following this performer.")
			return redirect(url_for('frontpage'))
		db.session.add(favorite_object)
		db.session.commit()
		flash("Successfully favorited " + str(performer.name))
		return redirect('/favorites')

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
		if unfavorite_object is None:
			flash("You are not following this performer.")
			return redirect(url_for('frontpage'))
		db.session.add(unfavorite_object)
		db.session.commit()
		flash("Successfully unfavorited " + str(performer.name))
		return redirect('/favorites')

@app.route('/search/performer', methods=['GET', 'POST'])
def searchperformer():
	form = PerformerSearchForm()
	g = form.validate_on_submit()
	if form.validate_on_submit():
		performer = Performer.query.filter_by(name=form.performername.data).first()
		return render_template('performerpage.html', performer=performer)
	return render_template('performersearch.html', form=form, g=g)

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
	for performance in Concert.query.all():
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
		if form.byperformer.data != "":
			performer = Performer.query.filter_by(name=form.byperformer.data).first()
			for performance in performer.performances:
				foundperformances.append(performance)
		else:
			foundperformances = Concert.query.all()

		if form.bydate.data is not None:
			for performance in foundperformances:
				if performance.date != form.bydate.data:
					foundperformances.remove(performance)
		if form.bystreetaddress.data != "":
			for performance in foundperformances:
				if performance.streetaddress != form.bystreetaddress.data:
					foundperformances.remove(performance)
		if form.bycity.data != "":
			for performance in foundperformances:
				if performance.city != form.bycity.data:
					foundperformances.remove(performance)
		if form.bystate.data != "":
			for performance in foundperformances:
				if performance.state != form.bystate.data:
					foundperformances.remove(performance)
		concerts = foundperformances
		return render_template('concerts.html', concerts=concerts)
	return render_template('searchconcerts.html', form=form)

@app.route('/createconcert', methods=['GET', 'POST'])
@login_required
def createconcert():
	if not current_user._get_current_object().isPerformer():
		flash("Non-performers cannot create concerts")
		return redirect(url_for('frontpage'))
	form = ConcertForm()
	if form.validate_on_submit():
		newconcert = Concert(form.date.data, form.time.data, form.streetaddress.data, form.city.data, form.state.data, current_user._get_current_object().performer_email)
		db.session.add(newconcert)
		db.session.commit()
		performers = []
		performers.append(current_user._get_current_object())
		if form.addperformers.data:
			names = form.addperformers.data
			names = names.replace(" ", "").split(",")
			for name in names:
				newperformer = Performer.query.get_or_404(name)
				performers.append(newperformer)
		for performer in performers:
			addperformerobject = newconcert.addPerformer(performer)
			db.session.add(addperformerobject)
			db.session.commit()
		flash("Concert created successfully")
		return redirect(url_for('frontpage'))
	return render_template('createconcert.html', form=form)

@app.route('/concerts/<performeremail>')
def concertsbyperformer(performeremail):
	performer = Performer.query.get_or_404(performeremail)
	concerts = performer.performances.all()
	return render_template('concerts.html', concerts=concerts)

@app.route('/edit/concert/<concert_id>', methods=['GET', 'POST'])
@login_required
def editconcert(concert_id):
	if not current_user._get_current_object().isPerformer():
		flash("Non-performers cannot edit concerts")
		return redirect(url_for('frontpage'))
	concert = Concert.query.get_or_404(concert_id)
	if current_user._get_current_object().performer_email != concert.owner:
		flash("Only the creator of the concert can modify it.")
	form = ConcertForm()
	if form.validate_on_submit():
		for performer in concert.performers.all():
			rmperfobject = concert.removePerformer(performer)
			db.session.add(rmperfobject)
			db.session.commit()
		performers = [current_user._get_current_object()]
		concert.date = form.date.data
		concert.time = form.time.data
		concert.streetaddress = form.streetaddress.data
		concert.city = form.city.data
		concert.state = form.state.data
		db.session.commit()
		if form.addperformers.data is not None:
			names = form.addperformers.data
			names = names.replace(" ", "").split(",")
			for name in names:
				newperformer = Performer.query.get_or_404(name)
				performers.append(newperformer)
		for performer in performers:
			addperfobject = concert.addPerformer(performer)
			if addperfobject is not None:
				db.session.add(concert.addPerformer(performer))
				db.session.commit()
		flash("Concert edited successfully")
		return redirect(url_for('frontpage'))
	form.date.data = concert.date
	form.time.data = concert.time
	form.streetaddress.data = concert.streetaddress
	form.city.data = concert.city
	form.state.data = concert.state
	performerstring = ""
	for performer in concert.performers:
		if performer.name != current_user._get_current_object().name:
			performerstring = performerstring + performer.name + ","
	performerstring = performerstring[:-1]
	form.addperformers.data = performerstring
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
		return render_template('test.html')
		return redirect(url_for('concerts', performeremail=performeremail))
	else:
		db.session.delete(concert)
		db.session.commit()
		flash("Concert successfully deleted")
		return redirect(url_for('concerts', performeremail=performeremail))
	