from flask.ext.wtf import Form
from wtforms.fields import StringField, BooleanField, PasswordField
from wtforms.validators import Required, ValidationError, Optional
from model import db, User, Performer, Concert

def uniquecheck(form, field):
	username = form.new_email_username.data
	person = User.query.get(username)
	if person is not None:
		raise ValidationError("Sorry, that email is already in use for an account.")

def uniqueperformercheck(form, field):
	username = form.new_email_username.data
	person = Performer.query.get(username)
	if person is not None:
		raise ValidationError("Sorry, that email is already in use for an account.")

def semiOptional(form, field):
	if field.data == "" and form.bycity.data == "" and form.bystate.data == "" and form.byperformer.data == "":
		raise ValidationError("Sorry, you must fill in at least one of the fields.")

def realPerformer(form, field):
	names = form.addperformers.data
	names = names.replace(" ", "").split(",")
	for name in names:
		if Performer.query.get(name) is None:
			raise ValidationError("Sorry, we have no record of that performer.")

def realPerformerName(form, field):
	pname = field.data
	if Performer.query.filter_by(name=pname).all() is None:
		raise ValidationError("Sorry, we have no record of that performer.")

def passwordCheck(form, field):
	username = form.email_username.data
	password = form.password.data

	if form.performer_option.data:
		person = Performer.query.get(username)
	else:
		person = User.query.get(username)


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
	addperformers = StringField('addperformers', validators=[realPerformer, Optional()])


class SignupForm(Form):
	new_email_username = StringField('new_email_username', validators=[Required(), uniquecheck])
	new_password = PasswordField('new_password', validators=[Required()])


class PerformerSignupForm(Form):
	new_email_username = StringField('new_email_username', validators=[Required(), uniqueperformercheck])
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
