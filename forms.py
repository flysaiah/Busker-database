from flask.ext.wtf import Form
from wtforms.fields import StringField, BooleanField, PasswordField
from wtforms.validators import Required, ValidationError
from model import db, User, Performer, Concert
from flask import render_template

#def uniquecheck(form, field):

def semiOptional(form, field):
	if field.data is None and form.bycity.data is None and form.bystate.data is None and form.byperformer.data is None:
		raise ValidationError("Sorry, you must fill in at least one of the fields.")

def realPerformer(form, field):
	names = form.addperformers.data
	if names is not None:
		names = names.replace(" ", "").split(",")
		for name in names:
			if Performer.query.get(name) is None:
				raise ValidationError("Sorry, we have no record of that performer.")

def realPerformerName(form, field):
	pname = field.data
	if pname is not None:
		if Performer.query.filter_by(name=pname).all() is None:
			raise ValidationError("Sorry, we have no record of that performer.")

def passwordCheck(form, field):
	username = form.email_username.data
	password = form.password.data

	if form.performer_option.data:
		person = Performer.query.get_or_404(username)
	else:
		person = User.query.get_or_404(username)


	if person is None:
		raise ValidationError("Sorry, we have no record of that username.")
	else:
		if not person.is_active():
			raise ValidationError("Sorry, we have no record of that username.")
		elif form.performer_option.data:
			if person.performer_password != password:
				raise ValidationError("Sorry, that password is incorrect.")
		else:
			if person.user_password != password:
				raise ValidationError("Sorry, that password is incorrect.")

class ConcertForm(Form):
	time = StringField('time', validators=[Required()])
	streetaddress = StringField('streetaddress', validators=[Required()])
	city = StringField('city', validators=[Required()])
	state = StringField('state', validators=[Required()])
	addperformers = StringField('addperformers', validators=[realPerformer])


class SignupForm(Form):
	new_email_username = StringField('new_email_username', validators=[Required()])
	new_password = PasswordField('new_password', validators=[Required()])


class PerformerSignupForm(Form):
	new_email_username = StringField('new_email_username', validators=[Required("This field is required.")])
	new_password = PasswordField('new_password', validators=[Required()])
	performer_name = StringField('performer_name', validators=[Required()])


class LoginForm(Form):
	email_username = StringField('email_username', validators=[Required()])
	password = PasswordField('password', validators=[Required(), passwordCheck])
	performer_option = BooleanField('performer_option')
	
class ConcertSearchForm(Form):
	byperformer = StringField('byperformer', validators=[realPerformerName])
	bystreetaddress = StringField('bystreetaddress', validators=[semiOptional])
	bycity = StringField('bycity')
	bystate = StringField('bystate')

class PerformerSearchForm(Form):
	performername = StringField('performername', validators=[Required(), realPerformerName])
