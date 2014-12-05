from flask.ext.wtf import Form
from wtforms.fields import StringField, BooleanField, PasswordField
from wtforms.validators import Required

class SignupForm(Form):
	new_email_username = StringField('new_email_username', validators=[Required()])
	new_password = PasswordField('new_password', validators=[Required()])
	performer_option = BooleanField('performer_option')
