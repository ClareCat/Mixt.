from app import app, client, db, login_manager
from contextlib import closing
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import EditForm, LoginForm, PreviewForm, RegisterForm, SourceForm, URLForm
from models import Metadata, Songs, Sources, User, Vote
from multiprocessing import Pool
import praw
from sqlalchemy import distinct, desc, func
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import soundcloud

@app.route('/')
def index():
	"""
	Does work for/renders index
	"""
	q = db.session.query(Songs.songurl, User.username, Songs.date, Songs.id, Songs.rating).join(Metadata, User).order_by(desc(Songs.rating)).limit(15).all()
	print q
	urls = [i[0] for i in q]
	g = parallel(urls, q)
	return render_template("genre.html", genre=g)

@app.route('/genre/<name>')
def genre(name):
	"""
	The <name> will be the name of the selected genre and will return all of the matching songs for that genre
	"""
	q = db.session.query(Songs.songurl, User.username, Songs.date, Songs.id, Songs.rating).join(Metadata, User).filter(func.lower(Metadata.genre)==func.lower(name)).order_by(desc(Songs.rating)).all()
	urls = [i[0] for i in q]
	g = parallel(urls, q)
	return render_template("genre.html", genre=g, name=name.title())

def parallel(urls, q):
	"""
	This function gets all the embed data and returns it as a list!
	Embed data is fetched in parallel
	"""
	numThreads = 9
	with closing(Pool(numThreads)) as p:
		urls = dict(zip(urls, p.map(get_embed_code, urls)))
	g = []
	for i in q:
		out_dict = {}
		curr = urls.get(i.songurl, None)
		if curr:
			out_dict["info"] = i
			out_dict["embed"] = curr
			g.append(out_dict)
	return g


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
	urlform = URLForm(request.form)
	pform = PreviewForm(request.form)
	sourceform = SourceForm(request.form)
	curr=True
	print sourceform.validate()
	if urlform.validate_on_submit() and not pform.validate_on_submit():
		track = get_track_info(urlform.url.data)
		pform.songname.data = track.title
		pform.artist.data = track.user['username']
		pform.label.data = track.label_name
		if pform.label.data is None:
			pform.label.data = ''
		pform.year.data = track.release_year
		if pform.year.data is None:
			pform.year.data = ''
		curr=False
	elif sourceform.validate_on_submit():
		add_source(sourceform.source.data, sourceform.genre.data)
		return redirect(url_for("index"))
	elif pform.validate_on_submit():
		add_track(pform.url.data, current_user.id, "user", pform.songname.data, pform.artist.data, pform.genre.data, pform.label.data, pform.year.data)
	return render_template("add.html", urlform=urlform, previewform=pform, sourceform=sourceform, curr=curr)

def get_track_info(url):
	track = client.get('/resolve', url=url)
	return track

def add_track(url, uploader, source, songname, artist, genre, label, year):
	dupe = db.session.query(Songs).filter(Songs.songurl==url).count()
	if dupe > 0:
		return None
	try:
		metadata = Metadata(artist, genre, label=label, year=year)
		db.session.add(metadata)
		db.session.commit()
		song = Songs(url, songname, uploader, source, metadata.id)
		db.session.add(song)
		db.session.commit()
		vote = Vote(current_user.id, song.id)
		db.session.add(vote)
		db.session.commit()
	except IntegrityError, e:
		print str(type(e)) + " " + str(e)
	except InvalidRequestError, e:
		print str(type(e)) + " " + str(e)

def add_source(source, genre):
	dupe = db.session.query(Sources).filter(Sources.subreddit==source).count()
	if dupe > 0:
		return None
	try:
		src = Sources(source, genre)
		db.session.add(src)
		db.session.commit()
	except Exception, e:
		print e

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
	print form.artist
	if form.validate_on_submit():
		if 'Delete' in request.form.values():
			votes = db.session.query(Vote).filter(Vote.songid==id).all()
			for vote in votes:
				db.session.delete(vote)
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
		metadata = db.session.query(Metadata).get(song.mid)
		return redirect(url_for("genre", name=metadata.genre))
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

@login_required
@app.route('/cron')
def reddit_update():
	r = praw.Reddit(user_agent=("Mixt./1.0 by ClareCat"))
	subreddits = db.session.query(Sources).filter(Sources.valid==True).all()
	for sub in subreddits:
		try:
			miss = True
			submissions = r.get_subreddit(sub.subreddit).get_hot()
			links = []
			for post in submissions:
				if "soundcloud" in post.url:
					miss = False
					track = get_track_info(post.url)
					add_track(post.url, current_user.id, "auto", track.title, track.user['username'], sub.genre, track.label_name, track.release_year)
			if miss:
				if sub.misses == 6:
					sub.set_valid(False)
				else:
					sub.increment_misses()
				db.session.commit()
		except praw.errors.InvalidSubreddit:
			sub.set_valid(False)
			db.session.commit()
		except Exception, e:
			print type(e)
			print e
	return redirect(url_for("index"))


	
	

