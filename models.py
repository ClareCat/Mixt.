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
    mid = db.Column(db.Integer, db.ForeignKey('metadata.id'), nullable=False)

    def __init__(self, songurl, name, uid, origin, mid):
        self.songurl = songurl
        self.uid = uid
        self.origin = origin
        self.votes = 0
        self.mid = mid
        self.name = name

    def __repr__(self):
        return '<Song %r>' % self.songurl