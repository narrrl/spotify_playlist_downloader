import os
import sys
import subprocess
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Credentials are now read from the .env file
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Set the folder where you want to save your tracks
DOWNLOAD_FOLDER = 'Spotify_Downloads'
# -------------------

def sanitize_filename(filename):
    """Removes illegal characters from a filename."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_playlist_tracks(playlist_url):
    """Fetches track titles and artist names from a Spotify playlist."""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("🛑 ERROR: CLIENT_ID or CLIENT_SECRET not found in .env file.")
        print("Please create a .env file with your Spotify credentials.")
        return []

    try:
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        print(f"🎵 Fetching tracks for playlist: {playlist_id}")

        results = sp.playlist_tracks(playlist_id)
        tracks_data = results['items']

        while results['next']:
            results = sp.next(results)
            tracks_data.extend(results['items'])
        
        # Extract title and first artist for each track
        tracks = []
        for item in tracks_data:
            if item['track']:
                track = item['track']
                title = track['name']
                artist = track['artists'][0]['name'] if track['artists'] else 'Unknown Artist'
                tracks.append({'title': title, 'artist': artist})
        
        print(f"✅ Found {len(tracks)} tracks in the playlist.")
        return tracks

    except Exception as e:
        print(f"An error occurred while fetching from Spotify: {e}")
        return []

def download_tracks(tracks, download_dir):
    """Searches and downloads tracks from YouTube using yt-dlp."""
    print(f"\n⏬ Starting downloads into '{download_dir}' folder...")
    os.makedirs(download_dir, exist_ok=True)
    
    total_tracks = len(tracks)
    for i, track in enumerate(tracks, 1):
        artist = track['artist']
        title = track['title']
        search_query = f"{artist} - {title}"
        safe_filename = sanitize_filename(search_query)
        output_path = os.path.join(download_dir, f"{safe_filename}.mp3")

        print(f"\n[{i}/{total_tracks}] Searching for: {search_query}")

        if os.path.exists(output_path):
            print(f"⏩ '{safe_filename}.mp3' already exists. Skipping.")
            continue

        try:
            command = [
                'yt-dlp', '--extract-audio', '--audio-format', 'mp3',
                '--audio-quality', '0', '--output', f"{os.path.join(download_dir, safe_filename)}.%(ext)s",
                '--no-playlist', '--quiet', '--progress', f"ytsearch1:{search_query}"
            ]
            
            subprocess.run(command, check=True)
            print(f"✅ Downloaded: {safe_filename}.mp3")

        except subprocess.CalledProcessError:
            print(f"❌ Failed to download: {search_query}. The video might be unavailable.")
        except Exception as e:
            print(f"An unexpected error occurred for '{search_query}': {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python spotify_downloader.py <spotify_playlist_url>")
    else:
        playlist_link = sys.argv[1]
        tracks_to_download = get_playlist_tracks(playlist_link)
        
        if tracks_to_download:
            download_tracks(tracks_to_download, DOWNLOAD_FOLDER)
            print("\n🎉 All tasks complete.")
