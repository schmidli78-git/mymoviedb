from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, RadioField, HiddenField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from .models import users, movies, genres

class LoginForm(FlaskForm):
        email = StringField('E-Mail', validators=[DataRequired()])
        password = PasswordField('Passwort', validators=[DataRequired()])
        remember_me = BooleanField('Angemeldet bleiben')
        submit = SubmitField('Anmelden')

class RegistrationForm(FlaskForm):
        displayname = StringField('Anzeigename', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired(), Email()])
        about = TextAreaField('Über mich')
        password = PasswordField('Passwort', validators=[DataRequired()])
        password2 = PasswordField(
                'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField('Registrieren')
        def validate_username(self, email):
                user = users.query.filter_by(email=email.data).first()
                if user is not None:
                        raise ValidationError('Bitte verwenden Sie einen anderen Benutzernamen.')
        def validate_email(self, email):
                user = users.query.filter_by(email=email.data).first()
                if user is not None:
                        raise ValidationError('Bitte verwenden Sie eine andere E-Mail Adresse.')
class EditProfileForm(FlaskForm):
        email = StringField('E-Mail', validators=[DataRequired()])
        displayname= StringField('Anzeigename', validators=[DataRequired()])
        about = TextAreaField('Über mich', render_kw={"rows": 8, "cols": 25}, validators=[Length(min=0, max=140)])
        submit = SubmitField('Speichern')

class CreateForm(FlaskForm):
        title = StringField('Titel', validators=[DataRequired()])
        description = TextAreaField('Beschreibung', render_kw={"rows": 8, "cols": 25}, validators=[DataRequired()])
        genreid= SelectField ('Genre', choices=[], coerce=int)
        duration = StringField('Abspieldauer (min)', validators=[DataRequired()])
        poster_path = HiddenField('Poster')
        backdrop_path = HiddenField('Backdrop')
        vote_average = HiddenField("Wertung auf IMDB")
        submit = SubmitField('Speichern')

class SearchForm(FlaskForm):
        title = StringField('Filmtitel', validators=[DataRequired()])
        submit = SubmitField('Suchen')

class RateForm(FlaskForm):
        rating = RadioField('Bewertung', choices=[(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)], coerce=int)
        text = TextAreaField('Beschreibung', validators=[DataRequired()])
        submit = SubmitField('Speichern')

class ListFilterForm(FlaskForm):
        search_title = StringField('Titel')
        search_genre= SelectField ('Genre', choices=[], coerce=int)
        search_sortorder= SelectField ('Sortierung', choices=[])
        submit = SubmitField('Filtern')