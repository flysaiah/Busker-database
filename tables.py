from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from mainfile import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buskerdb.db'
db = SQLAlchemy(app)

class Performer(db.Model):
	performer_email = db.Column(db.Text, primary_key=True)
	name = db.Column(db.Text)
	performer_password = db.Column(db.Text)

	def __init__(self, name, performer_email, performer_password):
		self.performer_email = performer_email
		self.name = name
		self.performer_password = performer_password)
	
	def __repr__(self):
		return '<Performer {0}>'.format(self.performer_email)	

class User(db.Model):
	user_email = db.Column(db.Text, primary_key=True)
	user_password = db.Column(db.Text)

	def __init__(self, user_email, user_password):
		self.user_email = user_email
		self.user_password = user_password
	def __repr__(self):
		return '<User {0}>'.format(self.user_email)

class Concert(db.Model):
	generated_id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.DateTime)
	place = db.Column(db.Text)
	owner = db.Column(db.Text)

	def __init__(self, time, place, owner):
		self.time = time
		self.place = place
		self.owner = owner
	def __repr__(self):
		return '<Concert at {0}, {1}>'.format(self.place, self.time)

performance = db.Table('performance', db.Column('email_of_performer', db.Text, db.ForeignKey('performer.performer_email')), db.Column('concert_id', db.Integer, db.ForeignKey('concert.generated_id')))

