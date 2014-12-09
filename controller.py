from flask import redirect
from tables import db, User, Performer, Concert

def validate_login(login_email, attempted_password):
	user = User.query.get_or_404(login_email)
	if attempted_password == user.password:
		return True
	return False

def delete_account(login_email):
	user = User.query.get_or_404(login_email)
	db.session.delete(user)
	db.session.confirm()
	return redirect('/accountdeleted')

