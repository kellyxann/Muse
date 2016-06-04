
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
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
app.secret_key = "ashortlifebutamerryone"
oauth = OAuth(app)

# Use Python os.environ to get environmental variables
# Note: you must run `source secrets.sh` on terminal before running
# this file to set required environmental variables.

musixmatch_api_key = os.environ['MUSIXMATCH_API_KEY']
spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
mapbox_api_key = os.environ['MAPBOX_API_KEY']
mapbox_pub_key = 'pk.eyJ1Ijoia2VsbHlhbm4iLCJhIjoiY2lvYmFqcnNlMDNwbnZ3bHpiZXlsYjVqbiJ9.0-hM3fi1TlEhf7pmXpfsrQ'

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
        return 'xAccess deniedx: {0}'.format(resp.message)

    session['oauth_token'] = (resp['access_token'], '')
    me = spotify.get('https://api.spotify.com/v1/me')
    session['user_id'] = me.data['id']
    print dir(me)
    print printer.pprint(me.data)
    return redirect('/dashboard')


@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


@app.route('/dashboard')
def show_dashboard():
    playlist_id = session.get('playlist_id')
    user_id = session['user_id']
    return render_template('dashboard.html', playlist_id=playlist_id, user_id=user_id)


@app.route('/create-keyword-playlist', methods=['POST'])
def create_keyword_playlist():
    """Creates a playlist for the user, and returns the playlist_id"""

    user_id = session['user_id']
    search_term = request.form.get('search_term')

    spotify_track_id_list = search_for_word_in_lyrics(search_term)

    playlist = spotify.post(
        'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
        data={'name': 'Muse--' + search_term},
        format='json')

    playlist_id = playlist.data['id']

    playlist_songs = spotify.post(
        'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(user_id, playlist_id),
        data={'uris': spotify_track_id_list},
        format='json')

    session['playlist_id'] = playlist_id

    return redirect('/dashboard')


@app.route('/create-location-playlist.json', methods=['POST'])
def create_location_playlist():
    """Creates a playlist for the user based upon their current location, and returns the playlist_id"""
    user_id = session['user_id']
    user_long = request.form.get('user_long')
    user_lat = request.form.get('user_lat')
    origin = request.form.get('origin')
    location_names = []
    location_track_list = []

    if origin is u'':
        location_names = get_location_info(user_long, user_lat)
    else:
        origin_coordinates = convert_to_coordinates(origin)
        origin_long = origin_coordinates[0]
        origin_lat = origin_coordinates[1]
        location_names = get_location_info(origin_long, origin_lat)

    playlist_name = location_names[-1] + ' ' + location_names[0]

    for name in location_names:
        location_track_list.extend(search_for_word_in_lyrics(name))

    playlist = spotify.post(
        'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
        data={'name': 'Muse--' + playlist_name },
        format='json')

    playlist_id = playlist.data['id']

    playlist_songs = spotify.post(
        'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(user_id, playlist_id),
        data={'uris': location_track_list},
        format='json')

    return jsonify({'user_id': user_id, 'playlist_id': playlist_id})



@app.route('/create-journey-playlist.json', methods=['POST'])
def create_journey_playlist():
    """Creates a playlist for the user, and returns the playlist_id"""
    user_id = session['user_id']
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    routing = request.form.get('routing')
    origin_coordinates = convert_to_coordinates(origin)
    origin_long = origin_coordinates[0]
    origin_lat = origin_coordinates[1]
    destination_coordinates = convert_to_coordinates(destination)
    destination_long = destination_coordinates[0]
    destination_lat = destination_coordinates[1]

    waypoint_names = []
    waypoint_track_ids = []

    r = requests.get('https://api.mapbox.com/directions/v5/mapbox/{}/{},{};{},{}.json?access_token={}&geometries=geojson&steps=true'.format(routing, origin_long, origin_lat, destination_long, destination_lat, mapbox_pub_key))
    response = r.json()

    for waypoint in response['waypoints']:
        waypoint_names.append(waypoint['name'])

    for step in response['routes'][0]['legs'][0]['steps']:
        waypoint_names.append(step['name'])

    count = 0
    for item in waypoint_names:
        while count < 5:
            count += 1
            waypoint_track_ids.extend(search_for_word_in_lyrics(item))

    playlist = spotify.post(
        'https://api.spotify.com/v1/users/{}/playlists'.format(user_id),
        data={'name': routing + ' to ' + destination },
        format='json')

    playlist_id = playlist.data['id']

    playlist_songs = spotify.post(
        'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(user_id, playlist_id),
        data={'uris': waypoint_track_ids},
        format='json')
    print playlist_songs

    data = {'user_id': user_id, 'playlist_id': playlist_id, 'directions': response}
    return jsonify(data)


    ####################### FIXME ####################
# i want to also send this back to my front end to have as a layer on the map




############################### HELPER FUNCTIONS ##############################


def search_for_word_in_lyrics(search_term):
    """Takes keyword input, and returns a list of spotify track ids
    for songs with that word or words in the lyrics"""

    payload = {'apikey': musixmatch_api_key, 'q_lyrics': search_term, 'page_size': '100'}
    # future feature: s_track_rating: asc or desc
    r = requests.get('http://api.musixmatch.com/ws/1.1/track.search', params=payload)
    data = r.json()
    # check to see that the URL has been correctly encoded by printing URL - print r.json() or print(r.url)
    spotify_track_id_list = []
    track_list = data['message']['body']['track_list']

    while len(spotify_track_id_list) < 10:
        for track in track_list:
            if track['track']['track_spotify_id']:
                spotify_track_id_list.append('spotify:track:' + track['track']['track_spotify_id'])

    return spotify_track_id_list


def convert_to_coordinates(place):
    """Given a place from user, return the [longitude, latitude]."""

    r =requests.get("https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json?autocomplete=true&access_token={}".format(place, mapbox_pub_key))
    data = r.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    return coordinates


def get_location_info(longitude, latitude):
    """Gets info about user's location to build a playlist using reverse geocoding"""

    r = requests.get('https://api.mapbox.com/geocoding/v5/mapbox.places/{}%2C{}.json?country=us&types=poi%2Caddress%2Cneighborhood%2Cpostcode%2Cregion%2Clocality%2Cplace%2Ccountry&autocomplete=true&access_token={}'.format(longitude, latitude, mapbox_pub_key))
    data = r.json()

    contexts = data['features'][0]['context']

    location_list = [context['text'] for context in contexts if context['id'].split('.')[0] in ('neighborhood', 'place', 'region')]
    # print data

    if data['features'][0]['text']:
        street_name = data['features'][0]['text']
        location_list.append(street_name)

    # if data['features'][0]['properties']['address']:
    #     street_name = data['features'][0]['properties']['address'].split()[1]
    #     location_list.append(street_name)

    return location_list

##############################################################################

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    # connect_to_db(app)
    app.run()
