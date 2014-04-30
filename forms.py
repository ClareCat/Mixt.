from app import db
from flask.ext.wtf import Form
from models import User
from sqlalchemy import and_
from wtforms import SelectField, TextField, PasswordField, validators

class LoginForm(Form):
	username = TextField('Username', [validators.Required()])
	password = PasswordField('Password', [validators.Required()])

	def get_user(self):
		u = db.session.query(User).filter(and_(User.username==self.username.data)).first()
		if u and u.check_password(self.password.data):
			return u
		else:
			return None

class URLForm(Form):
	url = TextField('SoundCloud URL', [validators.Required()])

class PreviewForm(Form):
	url = TextField('URL', [validators.Required()])
	songname = TextField('Songname', [validators.Required()])
	artist = TextField('Artist', [validators.Required()])
	album = TextField('Album')
	genre = SelectField('Genre', [validators.Required()], choices=[('Blues', 'blues'), ('Country','country'), ('Dubstep','dubstep'), ('Electronic', 'electronic'), ('Folk', 'folk'), ('Hiphop', 'hiphop'), ('House', 'house'), ('Jazz', 'jazz'), ('Pop', 'pop'), ('Rap', 'rap'), ('Rock', 'rock'), ('Trance', 'trance'), ('Trap', 'trap'), ('World', 'world')])
	label = TextField('Label')
	year = TextField('Year') 


class RegisterForm(Form):
	username = TextField('Username', [validators.Required()])
	password = PasswordField('Password', [validators.Required()])

	def check_reg(self):
		return db.session.query(User).filter_by(username=self.username.data).first()

class EditForm(Form):
	songname = TextField('Songname', [validators.Required()])
	artist = TextField('Artist', [validators.Required()])
	album = TextField('Album')
	genre = SelectField('Genre', [validators.Required()], choices=[('Blues', 'blues'), ('Country','country'), ('Dubstep','dubstep'), ('Electronic', 'electronic'), ('Folk', 'folk'), ('Hiphop', 'hiphop'), ('House', 'house'), ('Jazz', 'jazz'), ('Pop', 'pop'), ('Rap', 'rap'), ('Rock', 'rock'), ('Trance', 'trance'), ('Trap', 'trap'), ('World', 'world')])
	label = TextField('Label')
	year = TextField('Year')

class SourceForm(Form):
	source = TextField('Subreddit', [validators.Required()])
	genre = SelectField('Genre', [validators.Required()], choices=[('Blues', 'blues'), ('Country','country'), ('Dubstep','dubstep'), ('Electronic', 'electronic'), ('Folk', 'folk'), ('Hiphop', 'hiphop'), ('House', 'house'), ('Jazz', 'jazz'), ('Pop', 'pop'), ('Rap', 'rap'), ('Rock', 'rock'), ('Trance', 'trance'), ('Trap', 'trap'), ('World', 'world')])


