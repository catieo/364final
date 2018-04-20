# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, TextAreaField, IntegerField, PasswordField, SelectMultipleField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import json
import spotify_info_template

############################
# Application configurations
############################
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hard to guess string from si364'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/SI364projectplancatieo"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

########################
######## Models ########
########################

#association table between songs and playlists
user_playlist = db.Table('user_playlist',db.Column('user_id', db.Integer, db.ForeignKey('songs.id')),db.Column('playlists_id',db.Integer, db.ForeignKey('playlists.id')))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    playlists = db.relationship('Playlist', backref='User')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

## DB load function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None


class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    preview_url = db.Column(db.String(255))

    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id")) #one-to-many relationship: one artist, many songs

    def __repr__(self):
        return self.title


class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    songs = db.relationship('Song', backref='Artist')

    def __repr__(self):
        return self.name


class Playlist(db.Model):
    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    songs = db.relationship('Song',secondary=user_playlist,backref=db.backref('playlists',lazy='dynamic'),lazy='dynamic')

########################
######## Forms #########
########################
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log In')

class TypeForm(FlaskForm):
    type_of_search = StringField('Would you like recommendations based on an artist or a genre? Please enter \"artist\" or \"genre\":', validators=[Required()])
    submit = SubmitField('Get recommendations!')

    def validate_type_of_search(self,field):
        if (field.data != "artist") or (field.data != "genre"):
            raise ValidationError("Please enter \"artist\" or \"genre\" only.")

class ArtistForm(FlaskForm):
    artist = StringField("Enter your favorite artist: ", validators=[Required()])
    submit = SubmitField("Discover more songs like this artist!")

class GenreForm(FlaskForm):
    genre = StringField("Enter your favorite genre of music: ", validators=[Required()])
    submit = SubmitField("Discover new songs from this genre!")

class PlaylistForm(FlaskForm):
    name = StringField('What would you like to name your playlist? ',validators=[Required()])
    song_picks = SelectMultipleField('Pick the songs you\'d like to add!')
    submit = SubmitField("Save Playlist!")

    def validate_name(self, field):
        if Playlist.query.filter_by(name=field.data).first():
            raise ValidationError('Playlist name already taken')

class UpdateButtonForm(FlaskForm):
    submit = SubmitField("Update")

class UpdatePlaylistForm(FlaskForm):
    playlist_name = StringField('What would you like to rename your playlist?',validators=[Required()])
    submit = SubmitField("Update")

class DeleteButtonForm(FlaskForm):
    submit = SubmitField("Delete")


################################
####### Helper Functions #######
################################
def get_song_by_id(id):
    s = Song.query.filter_by(id=id).first()
    return s

def get_or_create_song(title, artist, url):
    s = Song.query.filter_by(title=title).first()
    if s:
        print("Song found")
        return s
    else:
        a = get_or_create_artist(artist)
        s = Song(title = title, preview_url=url, artist_id=a.id)
        db.session.add(s)
        db.session.commit()
        print("Song added")
        return s

def get_or_create_artist(artist_name):
    a = Artist.query.filter_by(name=artist_name).first()
    if a:
        return a
    else:
        artist = Artist(name=artist_name)
        db.session.add(artist)
        db.session.commit()
        return artist

def get_or_create_playlist(name, current_user, song_list=[]):
    p = Playlist.query.filter_by(name=name, user_id=current_user.id).first()
    if p:
        print('Playlist found')
        return p
    else:
        p = Playlist(name=name, user_id=current_user.id)
        for song in song_list:
            p.songs.append(song)
        db.session.add(p)
        db.session.commit()
        print("Playlist added")
        return p

def spotify_search_artist(search_term):
    base_url = 'https://api.spotify.com/v1/search'
    token = spotify_info_template.token
    headers = {'Authorization' : 'Bearer %s' % token,}
    url_params = {"q" : search_term, "type" : "artist"}
    results = requests.get(base_url, headers=headers, params=url_params)
    result_obj = json.loads(results.text)
    artist_id = result_obj['artists']['items'][0]['id']

    #browse query for recommendations based on an artist
    browse_url = 'https://api.spotify.com/v1/recommendations'
    browse_params = {"limit" : 10, "seed_artists" : artist_id}
    browse_results = requests.get(browse_url, headers=headers, params=browse_params)
    recs = json.loads(browse_results.text)
    song_list = []
    for song in recs['tracks']:
        song_list.append((song['name'], song['artists'][0]['name'], song['preview_url']))
    return song_list

def spotify_search_genre(search_term):
    browse_url = 'https://api.spotify.com/v1/recommendations'
    token = spotify_info_template.token
    headers = {'Authorization' : 'Bearer %s' % token,}
    browse_params = {"limit" : 10, "seed_genres" : search_term}
    browse_results = requests.get(browse_url, headers=headers, params=browse_params)
    recs = json.loads(browse_results.text)
    song_list = []
    for song in recs['tracks']:
        song_list.append((song['name'], song['artists'][0]['name'], song['preview_url']))
    return song_list


#TODO:
########################
#### View functions ####
########################

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

## Login-related routes
@app.route('/login',methods=["GET","POST"])
def login():
    # displays login form. if form validates, redirects to the previous page with 'next' or returns to '/'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    # logs out the current user. a link to this view function will be rendered on every page while a user is logged in. clicking this link will log the user out and return to '/'
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    # displays a form for a new user to register. if the form validates, redirect to '/login'
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

## Other routes
@app.route('/', methods=['GET', 'POST'])
def index():
    # display the song recommendation form (no login required). if form validates, invoke helper function to make api request and return song results
    form = TypeForm()
    if form.type_of_search.data == "artist":
        print("HELLO")
        return redirect(url_for('artist_search'))
    if form.type_of_search.data == "genre":
        return redirect(url_for('genre_search'))
    return render_template('index.html', form=form)

@app.route('/artist_search', methods=["GET", "POST"])
def artist_search():
    form = ArtistForm()
    if request.method == "POST":
        search_term = form.artist.data
        songs = spotify_search_artist(search_term)
        for song in songs:
            s = get_or_create_song(song[0],song[1],song[2])
        len_songs = len(songs)
        return render_template('search_results.html',songs=songs, len_songs=len_songs)
    return render_template('artist_search.html', form=form)

@app.route('/genre_search', methods=["GET", "POST"])
def genre_search():
    form = GenreForm()
    if form.validate_on_submit():
        search_term = form.genre.data
        songs = spotify_search_genre(search_term)
        for song in songs:
            s = get_or_create_song(song[0],song[1],song[2])
        len_songs = len(songs)
        return render_template('search_results.html', songs=songs, len_songs= len_songs)
    return render_template('genre_search.html', form=form)

@app.route('/all_songs')
def all_songs():
    # displays all songs currently saved in song table (any that have been returned as reults)
    all_songs = Song.query.all()
    return render_template('all_songs.html', all_songs=all_songs)

@app.route('/all_artists')
def all_artists():
    # displays all artists currently saved in the artists table. clicking on one of the artists will redirect to 'artist_songs/<artist_name>' for that artist
    all_artists = Artist.query.all()
    return render_template('all_artists.html', all_artists=all_artists)

@app.route('/artist_songs/<artist_name>')
def artist_songs(artist_name):
    # displays all songs by a specific artist that are currently saved in the song table
    # note to self: maybe figure out how to do this as an ajax request?
    artist = Artist.query.filter_by(name=artist_name).first()
    artist_songs = Song.query.filter_by(artist_id=artist.id).all()
    return render_template('artist_songs.html',songs=artist_songs,artist=artist)

@app.route('/create_playlist',methods=["GET","POST"])
@login_required
def create_playlist():
    # displays form that allows users to name a playlist and add songs to it. if form validates, playlist is created and user is redirected to a page that lists all of their playlists '/all_playlists'
    form = PlaylistForm()
    songs = Song.query.all()
    choices = [(s.id, s.title) for s in songs]
    form.song_picks.choices = choices

    if request.method == 'POST':
        selected_songs = form.song_picks.data
        print("SONGS SELECTED", selected_songs)
        song_objects = [get_song_by_id(int(id)) for id in selected_songs]
        print("SONGS RETURNED", song_objects)
        get_or_create_playlist(name=form.name.data, current_user=current_user, song_list=song_objects)
        return redirect(url_for('all_playlists'))
    return render_template('create_playlist.html', form=form)

@app.route('/all_playlists',methods=["GET","POST"])
@login_required
def all_playlists():
    # displays all of the current user's playlists with buttons to update the name of the playlist, or delete it that redirect to '/update_playlist/<playlist_name>' and '/delete_playlist/<playlist_name' respectively. clicking on a playlist will redirect the user to a page listing all of the songs on that playlist '/playlist/<id>'
    update_button = UpdateButtonForm()
    delete_button = DeleteButtonForm()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('all_playlists.html', playlists=playlists,update_button=update_button, delete_button=delete_button)


@app.route('/playlist/<id_num>')
@login_required
def playlist(id_num):
    # displays all of the songs on the specified playlist
    id_num = int(id_num)
    playlist = Playlist.query.filter_by(id=id_num).first()
    songs = playlist.songs.all()
    return render_template('playlist.html',playlist=playlist, songs=songs)

@app.route('/update_playlist/<playlist_name>', methods=["GET", "POST"])
@login_required
def update(playlist_name):
    # displays a form to update the name of the playlist. if form validates, user will be redirected to '/all_playlists'
    form = UpdatePlaylistForm()
    if form.validate_on_submit():
        new_name = form.playlist_name.data
        p = Playlist.query.filter_by(name=playlist_name,user_id=current_user.id).first()
        p.name = new_name
        db.session.commit()
        flash("Updated playlist name")
        return redirect(url_for('all_playlists'))
    return render_template('update_playlist.html', playlist_name=playlist_name, form=form)


@app.route('/delete_playlist/<playlist_name>', methods=["GET", "POST"])
@login_required
def delete(playlist_name):
    # deletes playlist and flashes a message telling this to the user. Redirects to '/all_playlists'
    p = Playlist.query.filter_by(name=playlist_name,user_id=current_user.id).first()
    db.session.delete(p)
    flash("Successfully deleted {}".format(playlist_name))
    return redirect(url_for('all_playlists'))


if __name__ == '__main__':
    db.create_all()
    manager.run()
