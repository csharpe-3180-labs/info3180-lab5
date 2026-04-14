# Add any model classes for Flask-SQLAlchemy here
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, first_name, last_name, username, password):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


# Helper function to update password for a user
def update_user_password(username, new_password):
    user = UserProfile.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        return True
    return False

class Movie(db.Model):
	__tablename__ = 'movies'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255), nullable=False)
	description = db.Column(db.Text, nullable=False)
	poster = db.Column(db.String(255), nullable=False)
	created_at = db.Column(db.DateTime, default=db.func.current_timestamp())