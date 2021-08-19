#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://benresnick@localhost:5432/fyyurapp'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))


    # implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))


#  implement any missing fields, as a database migration using Flask-Migrate

#  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    # Foreign Keys
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    # relationships
    artist = db.relationship(
        Artist,
        backref=db.backref('shows', cascade='all, delete')
    )
    venue = db.relationship(
        Venue,
        backref=db.backref('shows', cascade='all, delete')
    )


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #  replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('state').all()
    data = []
    for area in areas:
        venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).order_by('name').all()
        venue_data = []
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': venue_data
        })
        for venue in venues:
            shows = Show.query.filter_by(venue_id=venue.id).order_by('id').all()
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(shows)  #shows is still being properly implimented this is my
            })
    return render_template('pages/venues.html', areas=data)
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', None)
    venue_list = Venue.query.filter(
        Venue.name.ilike("%{}%".format(search_term))).all()
    response = {
        "count": len(venue_list),
        "data": venue_list
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replaced with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
    past_shows = []
    upcoming_shows = []
    for show in shows_query:
        artist = Artist.query.get(show.artist_id)
        temp_show = {
            'artist_id' : show.artist_id,
            'artist_name' : artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)
    data = {
        'id': venue_id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    data = request.form
    vname = data['name']
    vcity = data['city']
    vstate = data['state']
    vaddress = data['address']
    vphone = data['phone']
    vgenres = data.getlist('genres')
    vwebsite = data['website_link']
    vseeking_talent = data.get('seeking_talent')
    if vseeking_talent == "y":
        vseeking_talent = True;
    else:
        vseeking_talent = False;
    vfb_link = data['facebook_link']
    vimage_link = data['image_link']
    vseeking_description = data['seeking_description']
    try:
        db.session.add(Venue(
            name=vname,
            city=vcity,
            state=vstate,
            address=vaddress,
            phone=vphone,
            facebook_link=vfb_link,
            genres=vgenres,
            seeking_talent=vseeking_talent,
            website=vwebsite,
            image_link=vimage_link,
            seeking_description=vseeking_description
        ))
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        else:
            flash('An error occurred. Venue ' +
                  vname + ' could not be listed.')
            db.session.rollback()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    flash('something')
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Venue ' + venue_id + ' was deleted successfully!')
        else:
            flash('An error occurred. Deletion of Venue ' + venue_id + ' was unsuccessful.')
            db.session.rollback()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # replaced fake data with real data returned from querying the database
    artists = Artist.query.order_by('name').all()
    data = []
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implemented search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', None)
  artist_list = Artist.query.filter(
      Artist.name.ilike("%{}%".format(search_term))).all()
  response = {
      "count": len(artist_list),
      "data": artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).all()
    past_shows = []
    upcoming_shows = []
    for show in shows_query:
        venue = Venue.query.get(show.venue_id)
        temp_show = {
            'venue_id' : show.venue_id,
            'venue_name' : venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)
    data = {
        'id': artist_id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venues,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    # populated form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    artist = Artist.query.get(artist_id)
    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.website = request.form['website_link']
        artist.facebook_link = request.form['facebook_link']
        aseeking_venues = request.form.get('seeking_venue')
        if aseeking_venues == "y":
            artist.seeking_venues = True;
        else:
            artist.seeking_venues = False;
        artist.seeking_description = request.form['seeking_description']
        artist.image_link = request.form['image_link']
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was edited successfully!')
        else:
            flash('An error occurred. Artist ' + request.form['name'] + ' was not edited successfully.')
            db.session.rollback()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # populated form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    venue = Venue.query.get(venue_id)
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.website = request.form['website_link']
        venue.facebook_link = request.form['facebook_link']
        vseeking_talent = request.form.get('seeking_talent')
        if vseeking_talent == "y":
            venue.seeking_talent = True;
        else:
            venue.seeking_talent = False;
        venue.seeking_description = request.form['seeking_description']
        venue.image_link = request.form['image_link']
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was edited successfully!')
        else:
            flash('An error occurred. Venue ' + request.form['name'] + ' was not edited successfully.')
            db.session.rollback()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
    error = False
    data = request.form
    aname = data['name']
    acity = data['city']
    astate = data['state']
    aphone = data['phone']
    agenres = data.getlist('genres')
    awebsite = data['website_link']
    afacebook_link = data['facebook_link']
    aseeking_venues = data.get('seeking_venue')
    if aseeking_venues == "y":
        aseeking_venues = True;
    else:
        aseeking_venues = False;
    aseeking_description = data['seeking_description']
    aimage_link = data['image_link']
    try:
        db.session.add(Artist(
            name=aname,
            city=acity,
            state=astate,
            phone=aphone,
            genres=agenres,
            website=awebsite,
            facebook_link=afacebook_link,
            seeking_venues=aseeking_venues,
            seeking_description=aseeking_description,
            image_link=aimage_link
        ))
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            flash('An error occurred. Venue ' +
                  vname + ' could not be listed.')
            db.session.rollback()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # replace with real venues data.
    shows = Show.query.order_by('start_time').all()
    data = []
    for show in shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        data.append({
            'venue_id': show.venue_id,
            'venue_name': venue.name,
            'artist_id': show.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    data = request.form
    artist_id = data['artist_id']
    venue_id = data['venue_id']
    start_time = data['start_time']
    try:
        db.session.add(Show(
            artist_id = artist_id,
            venue_id = venue_id,
            start_time = start_time
        ))
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Show was successfully listed!')
        else:
            flash('An error occurred. Show could not be listed.')
            db.session.rollback()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
