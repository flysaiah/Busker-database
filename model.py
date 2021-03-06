from flask.ext.sqlalchemy import *
from app import db
from datetime import date
from flask import render_template

performances = db.Table('performances', db.Column('email_of_performer', db.Text, db.ForeignKey('performer.performer_email')), db.Column('concert_id', db.Integer, db.ForeignKey('concert.generated_id')))
favorites = db.Table('favorites', db.Column('p_email', db.Text, db.ForeignKey('performer.performer_email')), db.Column('u_email', db.Text, db.ForeignKey('user.user_email')))
attendings = db.Table('attendings', db.Column('email_of_user', db.Text, db.ForeignKey('user.user_email')), db.Column('id_of_concert', db.Integer, db.ForeignKey('concert.generated_id')))

class Performer(db.Model):
	performer_email = db.Column(db.Text, primary_key=True)
	name = db.Column(db.Text)
	performer_password = db.Column(db.Text)
	performances = db.relationship('Concert', secondary=performances, backref=db.backref('performers', lazy='dynamic'), lazy='dynamic')
	active = db.Column(db.Boolean)

	def __init__(self, performer_email, name, performer_password):
		self.performer_email = performer_email
		self.name = name
		self.performer_password = performer_password
		self.active = True
	
	def __repr__(self):
		return 'Performer {0}'.format(self.name)
	def is_authenticated(self):
		return True
	def is_active(self):
		return self.active
	def is_anonymous(self):
		return False
	def get_id(self):
		try:
			return unicode(self.performer_email)
		except NameError:
			return str(self.performer_email)
	def isPerformer(self):
		return True

class User(db.Model):
	user_email = db.Column(db.Text, primary_key=True)
	user_password = db.Column(db.Text)
	favorites = db.relationship('Performer', secondary=favorites, backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
	active = db.Column(db.Boolean)
	name = db.Column(db.Text)

	def __init__(self, user_email, user_password, name):
		self.user_email = user_email
		self.user_password = user_password
		self.name = name
		self.active = True
	def __repr__(self):
		return 'User {0}'.format(self.name)
	def is_authenticated(self):
		return True
	def is_active(self):
		return self.active
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
		concerts = []
		favorite_performers = self.favorites.all()
		for performer in favorite_performers:
			for concert in performer.performances.all():
				concerts.append(concert)
		return concerts
	def isPerformer(self):
		return False
	def attendConcert(self, concert):
		if not self.is_attending(concert):
			self.concerts.append(concert)
			return self
	def unattendConcert(self, concert):
		if self.is_attending(concert):
			self.concerts.remove(concert)
			return self
	def is_attending(self, concert):
		return self.concerts.filter(attendings.c.id_of_concert == concert.generated_id).count() > 0

class Concert(db.Model):
	generated_id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date)
	time = db.Column(db.Text)
	streetaddress = db.Column(db.Text)
	city = db.Column(db.Text)
	state = db.Column(db.Text)
	owner = db.Column(db.Text)
	attendees = db.relationship('User', secondary=attendings, backref=db.backref('concerts', lazy='dynamic'), lazy='dynamic')

	def __init__(self, date, time, streetaddress, city, state, owner):
		self.date = date
		self.time = time
		self.streetaddress = streetaddress
		self.city = city
		self.state = state
		self.owner = owner
	def __repr__(self):
		return 'Performance on {0} at {1} at {2}, {3}, {4}'.format(self.date, self.time, self.streetaddress, self.city, self.state)
	def addPerformer(self, performer):
		self.performers.append(performer)
		return self
	def removePerformer(self, performer):
		self.performers.remove(performer)
		return self