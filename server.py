# Muse is a project that allows a user to generate a Spotify playlist based upon
# a keyword search of a word or words that appear in the lyrics

# Optional features include auto-generating playlists based upon local weather,
# news headlines, and the Merriam Webster Word of the Day (or Dictionay.com),

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
    authorize_url='https://accounts.spotify.com/authorize'
)


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

    # future options: make a dictionary with artist name and song title fields to run through genius
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
        _external=True
    )

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
    return redirect('/create-playlist')

    # return 'yay for now\n\nLogged in as id={0} name={1} redirect={2}'.format(
    #     me.data['id'],
    #     me.data['name'],
    #     request.args.get('next')
    # )



@app.route('/create-playlist', methods=["GET", 'POST'])
def create_playlist():
    """Creates a playlist for the user, and returns the playlist_id"""
    user_id = session['user_id']
    print user_id

    if request.method == "POST":
        # the user submitted the form!
        search_term = request.form.get('search_term')
        # is this good use of shuffle?
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



@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')

def get_user_location():
    """Get a user's location based on their IP address"""

        send_url = 'http://freegeoip.net/json'
        r = requests.get(send_url)
        j = json.loads(r.text)
        user_lat = j['latitude']
        user_lon = j['longitude']

def convert_place_to_coordinates():
    """Given a place from user, return the longitude and latitude."""
    
    response = geocoder.forward('200 queen street')
    first = response.geojson()['features'][0]
    first['place_name']
    # returns '200 Queen St, Saint John, New Brunswick E2L 2X1, Canada' - this is what i'll want to put in the start search bar
    first['geometry']['coordinates']
    # returns long, lat as follows: [-66.050985, 45.270093]

https://api.mapbox.com/geocoding/v5/mapbox.places/.json?country=us&types=poi%2Caddress%2Cneighborhood%2Cpostcode%2Cregion%2Clocality%2Cplace%2Ccountry&autocomplete=true&access_token=sk.eyJ1Ijoia2VsbHlhbm4iLCJhIjoiY2lvZGt2cXY5MDA5MXU3a214OG0yZHN3YSJ9.WT2jodpnX-PNzvk2FlAZUw"
# if response contains "200 OK" else, flash a message telling them to try again
# send a get request to:
    # /geocoding/v5/mapbox.places/{query}.json
# query = a place name for forward geocoding to return long, latitude
query parameter - types: 'address, poi, place, postcode, locality, neighborhood, region'

results returned in a carmen geojson format
feature ids are formatted like {type}.{id}
check for presence of a value before attempting to use it



# def create_playlist_using_word_of_the_day:
#     """"""
# GET request to http://api.wordnik.com/v4/words.json/wordOfTheDay?api_key='yourkeyhere'
# returns the 'word of the day' object in json format


# in the future, reference an existing playlist id? e.g., weather factors, word of the day
# if/else statement - if it exists, link to playlist; else, create it
# playlist will follow the format 'mymuse-search_term'

# will cache data for word of the day
# will cache data for weather
# will store oauth token for users
# if time, create visualization
    # integrate D3 for visualization of other words? artist? genres?
    # use musixmatch to display lyrics?

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    # connect_to_db(app)
    app.run()
