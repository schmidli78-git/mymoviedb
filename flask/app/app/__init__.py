# app/__init__.py
import sqlalchemy
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from tmdbv3api import TMDb, Genre

from config import Config

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
loginmanager = LoginManager(app)
loginmanager.login_view = 'login'

#TheMovieDB API to grab content from
tmdb = TMDb()
tmdb.api_key = 'API_KEY_HERE'
tmdb.language = 'de'

if not app.debug:
    if not os.path.exists('/app/logs'):
        os.mkdir('/app/logs')
    file_handler = RotatingFileHandler('/app/logs/mymoviedb.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s: %(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MyMovieDB startup')

from app import routes, models, errors




