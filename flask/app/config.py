import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'DATABASE_URI_HERE'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MOVIES_PER_PAGE = 3
	# cyborg slate solar superhero
	# Available Templates cerulean,cosmo,cyborg,darkly,flatly,journal,litera,
	# lumen,lux,materia,minty,pulse,sandstone,simplex,sketchy,slate,solar,spacelab,superhero,united,yeti
	BOOTSTRAP_BOOTSWATCH_THEME = 'superhero'
