from flask import Flask, render_template, g, request, redirect, url_for, jsonify, session as flask_session
from chart import ChartScraper  # UK
import sqlite3
import string
from sqlalchemy import create_engine, Integer, String, Text, Column
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import requests
from spotify_playlist_creator import SpotifyPlaylistCreator


user_id = os.environ['SPOTIFY_USER_ID']
client_id = os.environ['SPOTIFY_CLIENT_ID']
client_secret = os.environ['SPOTIFY_SECRET_KEY']
redirect_uri = "http://localhost:8888/callback"

app = Flask(__name__)


def get_chart_data():
    num_items = 40

    scraper = ChartScraper()
    chart_data = scraper.get_chart_data(num_items)

    url = "https://spotify23.p.rapidapi.com/search/"
    headers = {
        "x-rapidapi-key": "8cb32d1ec0msh9e3669eb74e1b08p1d4c0bjsnb9f2bb7926a6",
        "x-rapidapi-host": "spotify23.p.rapidapi.com"
    }

    carousel_items = []

    for data in chart_data:
        querystring = {
            "q": "{} - {}".format(data.get('artist'), data.get('song')),
            "type": "multi",
            "offset": "0",
            "limit": "10",
            "numberOfTopResults": "5"
        }

        # Get the response and convert it to json format
        response = requests.get(url, headers=headers, params=querystring).json()

        # Extract the necessary data from the response
        try:
            # Extract track data
            track_data = response.get('topResults', {}).get('items')[0].get('data')

            artist_name = track_data.get('artists', {}).get('items')[0].get('profile', {}).get('name')
            artist_uri = track_data.get('artists', {}).get('items')[0].get('uri')

            track_name = track_data.get('name')
            track_uri = track_data.get('uri')

            # Extract the cover art url with width and height of 64
            for image in track_data.get('albumOfTrack', {}).get('coverArt', {}).get('sources', []):
                if image.get('width') == 64 and image.get('height') == 64:
                    cover_art_url = image.get('url')
                    break

            carousel_items.append({
                "artist_name": artist_name,
                "artist_uri": artist_uri,
                "track_name": track_name,
                "track_uri": track_uri,
                "cover_art_url": cover_art_url,
            })

        except (AttributeError, TypeError, IndexError):
            print(f"Could not extract information for {data.get('artist')} - {data.get('song')}")

    return carousel_items


@app.route("/")
def home():
    carousel_list = get_chart_data()
    for item in carousel_list:
        item["track_uri"] = item["track_uri"].replace("spotify:track:", "")
        # print(item["track_uri"])

    numbers = list(range(1, min(len(carousel_list), 40) + 1))
    carousel_data = list(zip(numbers, carousel_list[:40]))

    top_three = carousel_data[:3]

    playlist_creator = SpotifyPlaylistCreator(user_id, client_id, client_secret, redirect_uri)
    playlist_id = playlist_creator.create_playlist("OFFCHART")

    track_uris = [item['track_uri'] for item in carousel_list[:40]]
    successful_addition = playlist_creator.add_tracks_to_playlist(track_uris)
    if successful_addition:
        print(f"Successfully added {len(carousel_list)} tracks to playlist {playlist_id}")
        print(f'The playlist URI is {playlist_creator.get_playlist_uri()}')
    else:
        print('There was an error adding tracks to playlist')

    return render_template('index.html', carousel_list=carousel_data, top_three=top_three, playlist_id=playlist_creator.playlist_id)


if __name__ == '__main__':
    app.run(debug=True)
