# Muse is a project that allows a user to generate a Spotify playlist based upon
# a keyword search of a word or words that appear in the lyrics

# Optional features include auto-generating playlists based upon local weather,
# news headlines, and the Merriam Webster Word of the Day (or Dictionay.com),
# whichever API is better
# # import sys
# import sqlalchemy
# from flask import Flask, render_template, redirect, request, flash, session, jinja2
# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.secret_key = "thisshouldbeunguessable"

import requests
import os
# from pprint import pprint
# To access our OS environment variables
# Use Python os.environ to get environmental variables
# Note: you must run `source secrets.sh` on terminal before running
# this file to set required environmental variables.

musixmatch_api_key = os.environ['MUSIXMATCH_API_KEY']
print musixmatch_api_key


@app.route("/", methods = ['GET'])
def search_for_word_in_lyrics(search_term):
    """Takes a keyword or words input, and returns a Json object"""

search_term = request.form.get(search_term)

payload = {'apikey': musixmatch_api_key, 'q_lyrics': search_term, 's_track_rating': 'DESC'}
# 'q_track': search_term,
r = requests.get('http://api.musixmatch.com/ws/1.1/track.search', params=payload)

print r.json()

print(r.url)
# # check to see that the URL has been correctly encoded by printing URL

# word_songs = r.json()

# num_results = word_songs['resultCount']

# for i in range(num_results):
#     trackName=word_songs['results'][i].get('trackName')
#     artistName=word_songs['results'][i].get('artistName')
#     # print "track: %s, artist: %s" %(trackName, artistName)

# will cache data for word of the day
# will cache data for weather
# will store oauth token for users
# integrate D3 for visualization of other words? artist? genres?


# if __name__ == "__main__":
#     app.debug = True
#     app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
#     DebugToolbarExtension(app)
#     connect_to_db(app)
#     app.run()
