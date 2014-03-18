from app import db
from flask.ext.wtf import Form
from models import User
from sqlalchemy import and_
from wtforms import TextField, PasswordField, validators

class LoginForm(Form):
	username = TextField('Username', [validators.Required()])
	password = PasswordField('Password', [validators.Required()])

	def get_user(self):
		return db.session.query(User).filter(and_(User.username==self.username.data, User.password==self.password.data)).first()

class AddForm(Form):
	url = TextField('SoundCloud URL')

class RegisterForm(Form):
	username = TextField('Username', [validators.Required()])
	password = PasswordField('Password', [validators.Required()])

	def check_reg(self):
		return db.session.query(User).filter_by(username=self.username.data).first()



