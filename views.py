from app import app, client, db, login_manager
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import AddForm, EditForm, LoginForm, RegisterForm
from models import Metadata, Songs, User, Vote
import praw
from sqlalchemy import distinct, desc
from sqlalchemy.exc import IntegrityError, InvalidRequestError
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
	q = db.session.query(Songs.songurl, Songs.uid, Songs.date, Songs.id, Songs.rating).join(Metadata).filter(Metadata.genre==name).order_by(desc(Songs.rating))
	g = []
	for i in q:
		out_data = {}
		user = db.session.query(User.username).filter(User.id==i[1]).first()
		curr = get_embed_code(i[0])
		if curr:
			out_data["user"] = user[0]
			out_data["time"] = i[2]
			out_data["embed"] = curr
			out_data["id"] = i[3]
			out_data["rating"] = i[4]
			g.append(out_data)
	return render_template("genre.html", genre=g)

def get_embed_code(url):
	track_url = url
	try:
		embed_info = client.get('/oembed', url=track_url, maxheight=150)
		return embed_info.html
	except Exception, e:
		print e
		return None

@login_required
@app.route('/add', methods=['GET', 'POST'])
def add():
	form = AddForm(request.form)
	if form.validate_on_submit():
		errors = add_track(form.url.data, current_user.id, "user")
		if errors:
			print errors
		else:
			return redirect(request.args.get("next") or url_for("index"))
	return render_template("add.html", form=form)

def add_track(url, uploader, source):
	track = client.get('/resolve', url=url)
	try:
		if not track.genre:
			track.genre="Misc"
		metadata = Metadata(track.user['username'], track.genre, label=track.label_name, year=track.release_year)
		db.session.add(metadata)
		db.session.commit()
		song = Songs(url, track.title, uploader, source, metadata.id)
		db.session.add(song)
		db.session.commit()
		return None
	except AttributeError:
		return "Error getting link"
	except IntegrityError:
		return "OH NO DUPLICATE"
	except InvalidRequestError:
		return "WTF"

@login_required
@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
	q = db.session.query(Songs.id).filter(Songs.uid==current_user.id).all()
	u = []
	for i in q:
		d = {}
		song = db.session.query(Songs).get(i[0])
		meta = db.session.query(Metadata).get(song.mid)
		d['id'] = song.id
		d['name'] = song.name
		d['artist'] = meta.artist
		d['album'] = meta.album
		d['genre'] = meta.genre
		d['label'] = meta.label
		d['year'] = meta.year
		u.append(d)
	return render_template("uploads.html", uploads=u)

@login_required
@app.route('/uploads/edit/<id>', methods=['GET', 'POST'])
def edit(id):
	song = db.session.query(Songs).get(id)
	meta = db.session.query(Metadata).get(song.mid)
	form = EditForm(request.form, songname=song.name, artist=meta.artist, album=meta.album, genre=meta.genre, label=meta.label, year=meta.year)
	if form.validate_on_submit():
		if 'Delete' in request.form.values():
			db.session.delete(song)
			db.session.delete(meta)
			db.session.commit()
		else:
			song.name = form.songname.data
			meta.artist = form.artist.data
			meta.album = form.album.data
			meta.genre = form.genre.data
			meta.label = form.label.data
			meta.year = form.year.data
			db.session.commit()
		return redirect(url_for("uploads"))		
	return render_template("edit.html", form=form, songid=id)

@login_required
@app.route('/vote/<songid>', methods=['GET', 'POST'])
def vote(songid):
	userid = current_user.id
	duplicate = db.session.query(Vote).filter(Vote.songid==songid, Vote.uid == userid).all()
	if len(duplicate) == 0:
		vote = Vote(userid, songid)
		song = db.session.query(Songs).get(songid)
		song.increment_rating()
		db.session.add(vote)
		db.session.commit()
	return redirect(url_for("index"))


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

@app.route('/cron')
def reddit_update():
	r = praw.Reddit(user_agent=("Mixt./1.0 by ClareCat"))
	submissions = r.get_subreddit('electronicmusic').get_hot()
	links = []
	for post in submissions:
		if "soundcloud" in post.url:
			add_track(post.url, 2, "auto")
	



	
	

