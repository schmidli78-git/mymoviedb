# app/routes.py
#from pprint import pprint
#from inspect import getmembers
#from crypt import methods
import random
import json
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CreateForm, SearchForm, RateForm, ListFilterForm
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, flash, redirect, url_for, request, session, Response, escape
from math import ceil
from werkzeug.urls import url_parse
from .models import users, movies, genres, ratings
from app import db
from datetime import datetime
from tmdbv3api import Movie, Genre

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()

@app.route('/')
@app.route('/index')
def index():
	# tmdb API abfragen
	movie = Movie()
	popular = movie.popular()
	# Damit nicht immer die selben Filme angezeigt werden, werden Sie zufällig sortiert
	popular = random.sample(popular, len(popular))

	# Es werden i Objekte aus popular abgerufen und in mypop geschrieben.
	# Damit wird die Anzahl der auf der Startseite angezeigten "Schon gesehen?" Filme reduziert.
	i=0
	mypop=[]
	for p in popular:
		if p.overview != '':
			mypop.append(p)
			i= i+1
		if i == 4:
			break

	# Statistiken werden abgerufen
	stats = db.session.execute('''SELECT (SELECT count(*) FROM movies) as movies,
(SELECT count(*) FROM ratings) as ratings,
(SELECT count(*) FROM users) as users;''')

	# Die 10 am besten bewerteten Filme werden abgerufen
	resultset = db.session.execute('''SELECT m.id, m.title, m.poster_path, m.vote_average, FORMAT(IFNULL(avg(ratings.rating),0),1) as mymdb_avg,FORMAT(IFNULL(avg(ratings.rating),0),1)-1  as mysort, ( SELECT FORMAT(IFNULL(avg(rating),0),0) 
FROM ratings as r
WHERE r.userid = 2 AND r.movieid = m.id) AS userrating
FROM movies as m
LEFT JOIN ratings on(m.id=ratings.movieid)
JOIN genres on(genres.id=m.genreid)
GROUP BY m.id
ORDER BY mysort DESC, m.title
LIMIT 0,10
;''')

	# Daten werden an das Template weitergeleitet.
	return render_template('index.html', title='Schon gesehen?', user=user, popular=mypop, resultset=resultset, stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
	# Wenn der Benutzer bereits angemeldet ist, auf die Startseite weiterleiten
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	
	form = LoginForm()
	
	if form.validate_on_submit():
		
		# Überprüfung ob bereits ein User mit dieser E-Mail vorhanden ist
		user = users.query.filter_by(email=form.email.data).first()
		
		if user is None or not user.check_password(form.password.data):
			flash('Ungültige E-Mail Adresse oder Passwort')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next') # Rückkehr-Pfad
		
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)

	# Daten an das Template weiterleiten
	return render_template('login.html', title='Anmelden', form=form)

@app.route('/logout')
def logout():

	#Benutzer abmelden
	logout_user()

	# Umleiten auf Startseite
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = users(email=form.email.data, displayname=form.displayname.data, about=form.about.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Gratulation, Sie sind nun ein registrierter Benutzer!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Registrieren', form=form)

@app.route('/impressum')
def impressum():
	return render_template('impressum.html', title='Impressum')

@app.route('/user')
@app.route('/user/<int:userid>')
# Benutzer muss angemeldet sein
@login_required
def user(userid=0):
	if userid == 0:
		userid = current_user.id

	user = users.query.filter_by(id=userid).first_or_404()
	resultset = db.session.execute('''SELECT m.id, m.title, m.poster_path, m.vote_average, avg(ratings.rating) as mymdb_avg, r.rating, r.`text`
FROM movies as m 
JOIN ratings on(m.id=ratings.movieid)
JOIN genres on(genres.id=m.genreid)
JOIN ratings as r on(r.movieid=m.id)
WHERE r.userid = :u
GROUP BY m.id
;''',{'u':userid})

	return render_template('profile.html',title="Profil" ,user=user ,resultset=resultset)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.email = form.email.data
		current_user.displayname = form.displayname.data
		current_user.about = form.about.data
		db.session.commit()
		flash('Ihr Profil wurde gespeichert!')
		return redirect( url_for('edit_profile') )
	elif request.method == 'GET':
		form.email.data = current_user.email
		form.displayname.data = current_user.displayname
		form.about.data = current_user.about
	return render_template('edit_profile.html', title='Profil ändern', form=form)

@app.route('/list/', methods=['GET', 'POST'])
@app.route('/list/<int:page>', methods=['GET', 'POST'])
# Benutzer muss angemeldet sein
@login_required

def list(page=1):
	form = ListFilterForm()
	form.search_genre.choices = [(genres.id, genres.genre) for genres in genres.query.all()]
	form.search_sortorder.choices = [('ASC', 'Aufsteigend'),('DESC','Absteigend')]

	if "search_sortorder" in request.form:
		session['search_title'] = str(request.form.get("search_title")) 
		session['search_genre'] = int(request.form.get("search_genre"))
		session['search_sortorder'] = str(request.form.get("search_sortorder"))

	if "search_sortorder" in session:
		search_title = session['search_title'] 
		search_genre = int(session['search_genre'])
		search_sortorder = session['search_sortorder'] 
	else:
		search_title = ''
		search_genre = 0
		search_sortorder = 'ASC'

	#print(search_title,search_genre,search_sortorder)

	where_clause=''
	if search_title != '':
		where_clause = 'm.title LIKE "%' + search_title + '%"'
	if search_title != '' and search_genre != 0:
		where_clause += ' AND '
	if search_genre != 0:
		where_clause += 'm.genreid =' + str(search_genre)
	if where_clause != '':
		where_clause = 'WHERE ' + where_clause
	#print(where_clause)
	if search_sortorder == 'ASC':
		sortorder = 'ASC'
	else:
		sortorder = 'DESC'

	resultset = db.session.execute('''SELECT m.id, m.title, m.duration, m.poster_path, m.vote_average, genres.genre, FORMAT(IFNULL(avg(ratings.rating),0),1) as mymdb_avg, ( SELECT FORMAT(IFNULL(avg(rating),0),0) 
FROM ratings as r
WHERE r.userid = :u AND r.movieid = m.id) AS userrating
FROM movies as m
LEFT JOIN ratings on(m.id=ratings.movieid)
JOIN genres on(genres.id=m.genreid)
''' + where_clause + '''
GROUP BY m.id
ORDER BY m.title ''' + sortorder + '''
;''',{'u':current_user.id})

	page_limit = 10
	total_items = resultset.rowcount
	total_pages = int(ceil(total_items / page_limit))
	offset = (page * page_limit) - page_limit
	
	pages = db.session.execute('''SELECT m.id, m.title, m.duration, m.poster_path, m.vote_average, genres.genre, FORMAT(IFNULL(avg(ratings.rating),0),1) as mymdb_avg, ( SELECT FORMAT(IFNULL(avg(rating),0),0) 
FROM ratings as r
WHERE r.userid = :u AND r.movieid = m.id) AS userrating
FROM movies as m
LEFT JOIN ratings on(m.id=ratings.movieid)
JOIN genres on(genres.id=m.genreid)
''' + where_clause + '''
GROUP BY m.id
ORDER BY m.title ''' + sortorder + '''
LIMIT :o,10
;''',{'u':current_user.id,'o':offset})

	return render_template('list.html', title='Filme von A - Z', page=page, pages=pages, page_limit=page_limit, total_items=total_items, total_pages=total_pages, offset=offset, form=form, search_title=search_title, search_genre=search_genre, search_sortorder=search_sortorder )

@app.route('/detail/<movieid>/<page>', methods=['GET', 'POST'])
# Benutzer muss angemeldet sein
@login_required
def detail(movieid, page):
	movie = movies.query.filter_by(id=movieid).first()

	avg = db.session.execute('''SELECT FORMAT(IFNULL(avg(r.rating),0),1) as mymdb_avg
FROM ratings as r 
WHERE r.movieid = :i
GROUP BY r.movieid
;''',{'i':movieid })

	resultset = db.session.execute('''SELECT r.rating, r.`text`, u.id, u.displayname
FROM movies as m 
JOIN ratings on(m.id=ratings.movieid)
JOIN genres on(genres.id=m.genreid)
JOIN ratings as r on(r.movieid=m.id)
JOIN users as u on(u.id=r.userid)
WHERE m.id = :i
GROUP BY u.id
;''',{'i':movieid })

	return render_template('detail.html', title='Film Details', page=page, movie=movie, resultset=resultset, avg=avg)

@app.route('/delete/<movieid>/<page>', methods=['GET', 'POST'])
# Benutzer muss angemeldet sein
@login_required
def delete(movieid, page):
	ratings.query.filter_by(movieid=movieid).delete()
	db.session.commit()
	movies.query.filter_by(id=movieid).delete()
	db.session.commit()
	flash('Film wurde gelöscht!')
	return redirect(url_for('list', page=page))

@app.route('/create_search', methods=['GET', 'POST'])
def create_search():
	form = SearchForm()
	if form.validate_on_submit():
		movie = Movie()
		search = movie.search(form.title.data)
		print(search)
		return render_template('create_search.html', title='1. Suchen', user=user, search=search, form=form)
	return render_template('create_search.html', title='1. Suchen', user=user, form=form)

@app.route('/create/<movieid>', methods=['GET', 'POST'])
# Benutzer muss angemeldet sein
@login_required
def create(movieid):
	# 
	tmdb = Movie()
	tmdb_result = tmdb.details(movieid)

	form = CreateForm(poster_path=tmdb_result.poster_path)
	# Die Genres Auswahlliste wird mit Optionen aus der Datenbank befüllt 
	form.genreid.choices = [(genres.id, genres.genre) for genres in genres.query.all()]

	if form.validate_on_submit():
		#Formular Werte den Tabellenspalten zuweisen
		movie = movies(title=form.title.data, description=form.description.data, genreid=form.genreid.data, duration=form.duration.data, poster_path=form.poster_path.data, backdrop_path=form.backdrop_path.data, vote_average=form.vote_average.data, userid=current_user.id)
		#Prüfen ob ein solcher Film existiert
		check_exists = movies.query.filter_by(title=form.title.data).first()

		# Anhand von check_exists wird der Film gespeichert oder eine Fehlermeldung angezeigt
		if(not check_exists):
			db.session.add(movie)
			db.session.commit()
			flash('Sie haben einen neuen Film erfasst!','success')
			return redirect(url_for('create_search'))
		else:	
			flash('Dieser Film wurde bereits erfasst!','error')
			return redirect(url_for('create_search'))
	
	# Die Formularfelder aus der tmdb befüllen
	form.title.data = tmdb_result.title
	form.description.data = tmdb_result.overview
	form.duration.data = tmdb_result.runtime
	form.genreid.data = tmdb_result.genres[0].id
	form.poster_path.data = tmdb_result.poster_path
	form.backdrop_path.data = tmdb_result.backdrop_path
	form.vote_average.data = tmdb_result.vote_average

	# Daten an Template übergeben
	return render_template('create.html', title='3. Film speichern', form=form)

@app.route('/edit/<movieid>/<page>', methods=['GET', 'POST'])
# Benutzer muss angemeldet sein
@login_required
def edit(movieid,page):
	form = CreateForm()
	form.genreid.choices = [(genres.id, genres.genre) for genres in genres.query.all()]
	movie = movies.query.filter_by(id=movieid).first()

	if form.validate_on_submit():
		movie.title=form.title.data
		movie.description=form.description.data
		movie.genreid=form.genreid.data
		movie.duration=form.duration.data
		db.session.commit()
		flash('Änderungen wurden gespeichert!')
		return redirect(url_for('list',page=page))

	form.title.data = movie.title
	form.description.data = movie.description
	form.genreid.data = movie.genreid
	form.duration.data = movie.duration

	print(movie)

	return render_template('edit.html', title='Film bearbeiten', form=form)

@app.route('/rate/<movieid>/<page>', methods=['GET', 'POST'])
# Benutzer muss angemeldet sein
@login_required
def rate(movieid, page):
	form = RateForm()
	movie = movies.query.filter_by(id=movieid).first()
	rating = ratings.query.filter_by(userid=current_user.id, movieid=movieid).first()

	print(rating)

	if form.validate_on_submit():
		if not rating:
			rating = ratings(movieid=movie.id, userid=current_user.id, rating=form.rating.data, text=form.text.data)
			db.session.add(rating)
		else:
			rating.text=form.text.data
			rating.rating=form.rating.data
		db.session.commit()
		flash('Bewertung wurde gespeichert!')
		return redirect(url_for('list',page=page))

	if rating:
		form.text.data = rating.text
		form.rating.data = rating.rating

	return render_template('rate.html', title='Film bewerten', form=form)


@app.route('/api/get_movies')
def get_movies():

	#Alle Filme abfragen
	movies = db.session.execute('''SELECT m.id, m.title, m.description, m.duration, m.poster_path, m.backdrop_path, m.vote_average, genres.genre, FORMAT(IFNULL(avg(ratings.rating),0),1) as mymdb_avg
FROM movies as m
LEFT JOIN ratings on(m.id=ratings.movieid)
JOIN genres on(genres.id=m.genreid)
GROUP BY m.id
ORDER BY m.title DESC
;''').fetchall()
	ratings = db.session.execute('''SELECT *
FROM ratings as r
ORDER BY r.movieid DESC
;''').fetchall()


	# Filme und Ratings an das Template weitergeben, ausserdem wird der korrekte Mime-Type definiert
	return Response(render_template('api_get_movies.json', movies=movies, ratings=ratings), mimetype='application/json')


