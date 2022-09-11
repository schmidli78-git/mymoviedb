from datetime import datetime
from app import db
from flask_login import UserMixin
from app import loginmanager
from werkzeug.security import generate_password_hash, check_password_hash

@loginmanager.user_loader
def load_user(id):
    return users.query.get(int(id))

class users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    displayname = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(250))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.displayname)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(60))
    description = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    genreid = db.Column(db.Integer,db.ForeignKey('genres.id'))
    genre = db.relationship('genres')
    userid = db.Column(db.Integer,db.ForeignKey('users.id'))
    poster_path = db.Column(db.String(45))
    backdrop_path = db.Column(db.String(45))
    vote_average = db.Column(db.Integer)

    def __repr__(self):
        return '<Movie {}>'.format(self.title)

class genres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre= db.Column(db.String(45))

    def __repr__(self):
        return '<Genre {}>'.format(self.genre)

class ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('users.id'))
    movieid = db.Column(db.Integer,db.ForeignKey('movies.id'))
    rating= db.Column(db.Integer)
    text= db.Column(db.String)
    users = db.relationship(users,backref='ratings')
    movies = db.relationship(movies,backref='ratings')
    def __repr__(self):
        return '<Rating {}>'.format(self.rating)
