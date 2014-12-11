import mainfile

def get_current_user(l_proxy):
	if l_proxy.isPerformer:
		cu = mainfile.Performer.query.get(l_proxy.performer_email)
	else:
		cu = mainfile.User.query.get(l_proxy.user_email)
	return cu
