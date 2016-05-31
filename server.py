
from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_oauthlib.client import OAuth, OAuthException
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db
from random import shuffle
from mapbox import Geocoder
geocoder = Geocoder()
import subprocess
import requests
import mapbox
import json
import os
import sys
import pprint
printer = pprint.PrettyPrinter()

app = Flask(__name__)
app.secret_key = "thisshouldbeunguessable"
oauth = OAuth(app)

# Use Python os.environ to get environmental variables
# Note: you must run `source secrets.sh` on terminal before running
# this file to set required environmental variables.

musixmatch_api_key = os.environ['MUSIXMATCH_API_KEY']
spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
mapbox_api_key = os.environ['MAPBOX_API_KEY']

spotify = oauth.remote_app(
    'spotify',
    consumer_key=spotify_client_id,
    consumer_secret=spotify_client_secret,
    request_token_params={'scope': 'playlist-modify-public user-read-email user-read-private user-read-birthdate'},
    base_url='https://accounts.spotify.com/',
    # request_token_url='https://accounts.spotify.com/api/token',
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize')


@app.route('/')
def start_here():
    """Greet user, introduce the App, and display a button to login to Spotify."""

    return render_template('homepage.html')


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        # next=request.args.get('next') or request.referrer or None,
        next=None,
        _external=True)
    return spotify.authorize(callback=callback)


@app.route('/login/authorized')
def spotify_authorized():
    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'xAccess denied: {0}'.format(resp.message)

    session['oauth_token'] = (resp['access_token'], '')
    me = spotify.get('https://api.spotify.com/v1/me')
    session['user_id'] = me.data['id']
    print dir(me)
    print printer.pprint(me.data)
    return redirect('/dashboard.html')

# is dashboard.html where this redirects?

@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')

@app.route('/dashboard')
def show_dashboard():
    return render_template('dashboard.html')


@app.route('/create-location-playlist', methods=['POST'])
def create_location_playlist():
    """Creates a playlist for the user based upon their current location, and returns the playlist_id"""
    user_id = session['user_id']
    print user_id
    location = request.form.get('location')

    location_names = get_location_info(location)




@app.route('/create-journey-playlist', methods=['POST'])
def create_journey_playlist():
    """Creates a playlist for the user, and returns the playlist_id"""
    user_id = session['user_id']
    print user_id
    origin, destination, routing = request.form.get('origin', 'destination', 'routing')
    origin = convert_to_coordinates(origin)
    destination = convert_to_coordinates(destination)

    coordinates = 
        if routing == 'walking'
            GET https://api.mapbox.com/directions/v5/mapbox/walking/{coordinates}

        if routing == 'cycling'
            GET https://api.mapbox.com/directions/v5/mapbox/cycling/{coordinates}

        if routing == 'driving'
            GET https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates}


@app.route('/create-keyword-playlist', methods=["GET", 'POST'])
def create_keyword_playlist():
    """Creates a playlist for the user, and returns the playlist_id"""
    user_id = session['user_id']
    print user_id

    if request.method == "POST":
        # the user submitted the form!
        search_term = request.form.get('search_term')
        spotify_track_id_list = shuffle(search_for_word_in_lyrics(search_term))
        playlist = spotify.post(
            'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
            data={'name': 'Muse--' +search_term},
            format='json')
        playlist_id = playlist.data['id']
        print "playlist_id:" +playlist_id

        playlist_songs = spotify.post(
            'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(user_id, playlist_id),
            data={'uris': spotify_track_id_list},
            format='json')
        print playlist_songs
        return render_template('player.html', user_id=user_id, playlist_id=playlist_id)
    else:
        # just show the form
        return render_template('player.html', user_id=user_id, playlist_id=None)


def search_for_word_in_lyrics(search_term):
    """Takes keyword input, and returns a list of spotify track ids
    for songs with that word or words in the lyrics"""

    # search_term = request.form.get(search_term)

    payload = {'apikey': musixmatch_api_key, 'q_lyrics': search_term, 'page_size': '100'}
# s_track_rating: asc or desc
    r = requests.get('http://api.musixmatch.com/ws/1.1/track.search', params=payload)
    data = r.json()

# check to see that the URL has been correctly encoded by printing URL
# print r.json()
# print(r.url)

    spotify_track_id_list = []
    track_list = data ['message']['body']['track_list']

    for track in track_list:
        if track['track']['track_spotify_id']:
            spotify_track_id_list.append('spotify:track:' + track['track']['track_spotify_id'])
    return spotify_track_id_list




def convert_to_coordinates(place):
    """Given a place from user, return the longitude and latitude."""

    r =requests.get("https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json".format(place))
    data = r.json()


    response = geocoder.forward('200 queen street')
    first = response.geojson()['features'][0]
    first['place_name']
    # returns '200 Queen St, Saint John, New Brunswick E2L 2X1, Canada' - this is what i'll want to put in the start search bar
    first['geometry']['coordinates']
    # returns long, lat as follows: [-66.050985, 45.270093]

def get_location_info(location):
    """Gets info about user's location to build a playlist"""
    r = requests.get('https://api.mapbox.com/geocoding/v5/mapbox.places/?country=us&types=poi%2Caddress%2Cneighborhood%2Cpostcode%2Cregion%2Clocality%2Cplace%2Ccountry&autocomplete=true&access_token=pk.eyJ1Ijoia2VsbHlhbm4iLCJhIjoiY2lvYmFqcnNlMDNwbnZ3bHpiZXlsYjVqbiJ9.0-hM3fi1TlEhf7pmXpfsrQ'
# if response contains "200 OK" else, flash a message telling them to try again
# send a get request to:
    # /geocoding/v5/mapbox.places/{query}.json
# query = a place name for forward geocoding to return long, latitude
query parameter - types: 'address, poi, place, postcode, locality, neighborhood, region'

results returned in a carmen geojson format
feature ids are formatted like {type}.{id}
check for presence of a value before attempting to use it



if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    # connect_to_db(app)
    app.run()
