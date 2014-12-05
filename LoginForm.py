from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField
from wtforms.validators import Required


class LoginForm(Form):
	email_username = StringField('email_username', validators=[Required()])
	password = PasswordField('password', validators=[Required()])
	