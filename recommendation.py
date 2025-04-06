import requests
import base64
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

spotify_playlist = {
    "weekly most stream":{
        "Global":"37i9dQZEVXbNG2KDcFcKOF",
        "America":"37i9dQZEVXbLp5XoPON0wI",
        "Taiwan":"37i9dQZEVXbMVY2FDHm6NN",
        "Japan":"37i9dQZEVXbKqiTGXuCOsB"},
    "daily most stream":{
        "Global":"37i9dQZEVXbMDoHDwVN2tF",
        "America":"37i9dQZEVXbLRQDuF5jeBp",
        "Taiwan":"37i9dQZEVXbMnZEatlMSiu",
        "Japan":"37i9dQZEVXbKXQ4mDTEBXq"}
    }


CLIENT_ID = 'ID'
CLIENT_SECRET = 'SECRET'


client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
client_credentials_base64 = base64.b64encode(client_credentials.encode())


token_url = 'https://accounts.spotify.com/api/token'
headers = {
    'Authorization': f'Basic {client_credentials_base64.decode()}'
}
data = {
    'grant_type': 'client_credentials'
}
response = requests.post(token_url, data=data, headers=headers)

if response.status_code == 200:
    access_token = response.json()['access_token']
    print("Access token obtained successfully.")
else:
    print("Error obtaining access token.")
    exit()
    
def get_recommendation(playlist_id):
    # Set up Spotipy with the access token
    sp = spotipy.Spotify(auth=access_token)

    # Get the tracks from the playlist
    playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id, name, artists, album(id, name)))')

    # Extract relevant information and store in a list of dictionaries
    playlist = []
    for track_info in playlist_tracks['items']:
        track = track_info['track']
        track_id = track['id']

        # Get popularity of the track
        try:
            track_info = sp.track(track_id) if track_id != 'Not available' else None
            popularity = track_info['popularity'] if track_info else None
        except:
            popularity = None

        playlist.append(track_info.get('external_urls', {}).get('spotify', None))

    return playlist

def playlist_exist(playlist_id):
    sp = spotipy.Spotify(auth=access_token)
    try:
        playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id, name, artists, album(id, name)))')
        return True
    except:
        return False

def auto_suggestion(mode,location):
    if mode == "custom":
        playlist = get_recommendation(location)
        x = random.randint(0,len(playlist)-1)
    else:
        playlist = get_recommendation(spotify_playlist[mode][location])
        x = random.randint(0,len(playlist)-1)
    return playlist[x]