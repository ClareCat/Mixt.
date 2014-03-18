from app import app, client, db, login_manager
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import AddForm, LoginForm, RegisterForm
from models import Metadata, Songs, User
from sqlalchemy import distinct
import soundcloud


@app.route('/')
def index():
	"""
	Does work for/renders index
	"""
	g = get_genres()
	print g
	return render_template("index.html", genres=g)

@app.route('/genre/<name>')
def genre(name):
	"""
	The <name> will be the name of the selected genre and will return all of the matching songs for that genre
	"""
	return "Genres page"

@login_required
@app.route('/add', methods=['GET', 'POST'])
def add():
	form = AddForm(request.form)
	if form.validate_on_submit():
		track = client.get('/resolve', url=form.url.data)
		metadata = Metadata(track.user['username'], track.genre, label=track.label_name, year=track.release_year)
		db.session.add(metadata)
		db.session.commit()
		song = Songs(form.url.data, track.title, current_user.id, "user", metadata.id)
		db.session.add(song)
		db.session.commit()
		return redirect(request.args.get("next") or url_for("index"))
	return render_template("add.html", form=form)
	

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm(request.form)
	if form.validate_on_submit():
		user = form.get_user()
		if user:
			login_user(user)
			flash("Logged in successfully.")
			return redirect(request.args.get("next") or url_for("index"))
	return render_template("login.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if form.validate_on_submit():
		reg = form.check_reg()
		if not reg:
			user = User(form.username.data, form.password.data)
			db.session.add(user)
			db.session.commit()
			return redirect(request.args.get("next") or url_for("login"))
	return render_template("register.html", form=form)

@login_required
@app.route('/logout/')
def logout_view():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(userid):
	return User.query.get(userid)

def get_genres():
	q = db.session.query(distinct(Metadata.genre)).all()
	return [i[0] for i in q]
	
	

