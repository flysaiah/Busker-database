import mainfile


mainfile.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buskerdb.db'
db = SQLAlchemy(app)

performances = db.Table('performances', db.Column('email_of_performer', db.Text, db.ForeignKey('performer.performer_email')), db.Column('concert_id', db.Integer, db.ForeignKey('concert.generated_id')))
favorites = db.Table('favorites', db.Column('p_email', db.Text, db.ForeignKey('performer.performer_email')), db.Column('u_email', db.Text, db.ForeignKey('user.user_email')))
attendings = db.Table('attendings', db.Column('email_of_user', db.Text, db.ForeignKey('user.user_email')), db.Column('id_of_concert', db.Integer, db.ForeignKey('concert.generated_id')))

class Performer(db.Model):
	performer_email = db.Column(db.Text, primary_key=True)
	name = db.Column(db.Text)
	performer_password = db.Column(db.Text)
	performances = db.relationship('Concert', secondary=performances, backref='performers')

	def __init__(self, performer_email, name, performer_password):
		self.performer_email = performer_email
		self.name = name
		self.performer_password = performer_password
	
	def __repr__(self):
		return '<Performer {0}>'.format(self.performer_email)
	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		try:
			return unicode(self.performer_email)
		except NameError:
			return str(self.performer_email)

class User(db.Model):
	user_email = db.Column(db.Text, primary_key=True)
	user_password = db.Column(db.Text)
	favorites = db.relationship('Performer', secondary=favorites, backref='followers')

	def __init__(self, user_email, user_password):
		self.user_email = user_email
		self.user_password = user_password
	def __repr__(self):
		return '<User {0}>'.format(self.user_email)
	def is_authenticated(self):
		return True
	def is_active(self):
		return True
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

class Concert(db.Model):
	generated_id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Text)
	place = db.Column(db.Text)
	owner = db.Column(db.Text)
	attendees = db.relationship('User', secondary=attendings, backref='concerts')

	def __init__(self, time, place, owner):
		self.time = time
		self.place = place
		self.owner = owner
	def __repr__(self):
		return '<Concert at {0}, {1}>'.format(self.place, self.time)
