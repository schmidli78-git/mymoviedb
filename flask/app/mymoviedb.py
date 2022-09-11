from app import app, db
from app.models import users, movies, genres



if __name__ == '__main__':
    app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))
    app.run(host='0.0.0.0')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': users, 'Movie': movies, 'Genre': genres}
