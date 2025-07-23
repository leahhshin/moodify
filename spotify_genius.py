import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()


## spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")

## genius
GENIUS_API_KEY = os.getenv("GENIUS_KEY")

SPOTIFY_SCOPE= "user-read-recently-played"

import lyricsgenius

genius = lyricsgenius.Genius(GENIUS_API_KEY)

def get_lyrics_from_genius(artist_name, track_name):
    try:
        song = genius.search_song(track_name, artist_name)
        if song:
            return song.lyrics
        else:
            return None
    except Exception as e:
        print(f"Error fetching lyrics for {track_name} by {artist_name}: {e}")
        return None

def get_recently_played_songs():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri='http://localhost:8888/callback',
            scope=SPOTIFY_SCOPE
        )
    )
    
    results = sp.current_user_recently_played(limit=50)
    tracks_data = []
    seen_tracks = set()  # To track unique songs by track ID
    
    for item in results['items']:
        track = item['track']
        track_id = track['id']

        if track_id in seen_tracks:
            continue  # Skip duplicates
        
        seen_tracks.add(track_id)  # Mark track as seen

        track_info = {
            'track_name': track['name'],
            'artist_name': track['artists'][0]['name'],
            'album_name': track['album']['name'],
            'track_id': track_id
        }

        lyrics = get_lyrics_from_genius(track_info['artist_name'], track_info['track_name'])
        track_info['lyrics'] = lyrics 
        tracks_data.append(track_info)
        
    return tracks_data


