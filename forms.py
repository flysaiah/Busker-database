from flask.ext.wtf import Form
from wtforms.fields import StringField, BooleanField, PasswordField
from wtforms.validators import Required, ValidationError
import mainfile


def passwordCheck(form, field):
	username = form.email_username.data
	password = form.password.data

	if form.performer_option.data:
		person = mainfile.Performer.query.get(username)
	else:
		person = mainfile.User.query.get(username)

	if person is None:
		raise ValidationError("Sorry, we have no record of that username.")
	elif person.password != password:
		raise ValidationError("Sorry, that password is incorrect.")




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
	

