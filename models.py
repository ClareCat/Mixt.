from app import db
from datetime import datetime
from flask.ext.login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    access = db.Column(db.String(2), nullable=False, default=0)
    join = db.Column(db.DateTime, nullable=False)
    user = db.relationship('Songs', backref=db.backref('user'))

    def __init__(self, username, password):
        # THIS IS NOT SECURE...like at all
        self.username = username
        self.password = password
        self.join = datetime.utcnow()

    def __repr__(self):
        return '<User %r>' % self.username

class Metadata(db.Model):
    __tablename__ = "metadata"
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(40), nullable=False)
    album = db.Column(db.String(40))
    genre = db.Column(db.String(20), nullable=False)
    label = db.Column(db.String(120))
    year = db.Column(db.String(4))
    metaid = db.relationship('Songs', backref=db.backref('metadata'))

    def __init__(self, artist, genre, album=None, label=None, year=None):
        self.artist = artist
        self.album = album
        self.genre = genre
        self.label = label
        self.year = year

    def __repr__(self):
        return '<Meta %r>' % self.artist

class Songs(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    songurl = db.Column(db.String(120), nullable=False, unique=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    votes = db.Column(db.Integer)
    origin = db.Column(db.String(5))
    date = db.Column(db.DateTime)
    rating = db.Column(db.Integer)
    mid = db.Column(db.Integer, db.ForeignKey('metadata.id'), nullable=False)

    def __init__(self, songurl, name, uid, origin, mid):
        self.songurl = songurl
        self.uid = uid
        self.origin = origin
        self.votes = 0
        self.mid = mid
        self.name = name
        self.date = datetime.utcnow()
        self.rating = 1

    def __repr__(self):
        return '<Song %r>' % self.songurl

    def increment_rating(self):
        self.rating += 1

class Vote(db.Model):
    __tablename__ = "vote"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time = db.Column(db.DateTime)
    songid = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)

    def __init__(self, uid, songid):
        self.uid = uid
        self.songid = songid
        self.time = datetime.utcnow()

class Sources(db.Model):
    __tablename__ = "sources"
    id = db.Column(db.Integer, primary_key=True)
    subreddit = db.Column(db.String(50), nullable=False, unique=True)
    date = db.Column(db.DateTime)
    valid = db.Column(db.Boolean, nullable=False, default=True)
    misses = db.Column(db.Integer, nullable=False, default=0)
    genre = db.Column(db.String(20), nullable=False)

    def __init__(self, subreddit, genre):
        self.subreddit = subreddit
        self.date = datetime.utcnow()
        self.genre = genre

    def set_valid(self, valid):
        self.valid = valid

    def increment_misses(self):
        self.misses += 1


