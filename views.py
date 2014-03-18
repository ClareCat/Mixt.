from app import app, client, db, login_manager
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import AddForm, EditForm, LoginForm, RegisterForm
from models import Metadata, Songs, User
from sqlalchemy import distinct
import soundcloud


@app.route('/')
def index():
	"""
	Does work for/renders index
	"""
	q = db.session.query(distinct(Metadata.genre)).all()
	g = [i[0] for i in q]
	return render_template("index.html", genres=g)

@app.route('/genre/<name>')
def genre(name):
	"""
	The <name> will be the name of the selected genre and will return all of the matching songs for that genre
	"""
	q = db.session.query(Songs.songurl).join(Metadata).filter(Metadata.genre==name).all()
	g = [get_embed_code(i[0]) for i in q]
	return render_template("genre.html", genre=g)

def get_embed_code(url):
	track_url = url
	print track_url
	embed_info = client.get('/oembed', url=track_url, maxheight=150, show_comments="false")
	return embed_info.html

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
	
@login_required
@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
	q = db.session.query(Songs.name).filter(Songs.uid==current_user.id).all()
	u = [i[0] for i in q]
	return render_template("uploads.html", uploads=u)

@login_required
@app.route('/uploads/edit/<name>', methods=['GET', 'POST'])
def edit(name):
	song = db.session.query(Songs.mid, Songs.name, Songs.songurl).filter(Songs.name==name).first()
	print song
	meta = db.session.query(Metadata).get(song.mid)
	form = EditForm(request.form, songname=song.name, artist=meta.artist, album=meta.album, genre=meta.genre, label=meta.label, year=meta.year)
	if form.validate_on_submit():
		song.name = form.songname.data
		meta.artist = form.artist.data
		meta.album = form.album.data
		meta.genre = form.genre.data
		meta.label = form.label.data
		meta.year = form.year.data
		db.session.commit()
		return redirect(url_for("uploads"))		
	return render_template("edit.html", form=form, name=name)

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



	
	

