import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# This scope allows the script to read and modify your followed artists
SCOPE = "user-follow-modify"
# -------------------

def get_unique_artist_ids(sp, playlist_url):
    """
    Fetches all tracks from a playlist and returns a set of unique artist IDs.
    """
    try:
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        print(f"🎵 Fetching artists for playlist: {playlist_id}")

        results = sp.playlist_tracks(playlist_id)
        tracks_data = results['items']

        # Handle paginated playlists
        while results['next']:
            results = sp.next(results)
            tracks_data.extend(results['items'])

        artist_ids = set()
        for item in tracks_data:
            if item['track']:
                for artist in item['track']['artists']:
                    artist_ids.add(artist['id'])
        
        print(f"✅ Found {len(artist_ids)} unique artists in the playlist.")
        return list(artist_ids)

    except Exception as e:
        print(f"An error occurred while fetching artists: {e}")
        return []

def follow_artists_in_batches(sp, artist_ids):
    """
    Follows a list of artists in batches of 50.
    """
    if not artist_ids:
        print("No new artists to follow.")
        return

    print(f"\n⏬ Starting to follow {len(artist_ids)} artists...")
    
    # Spotify API can handle a maximum of 50 IDs per request
    batch_size = 50
    followed_count = 0
    
    for i in range(0, len(artist_ids), batch_size):
        batch = artist_ids[i:i + batch_size]
        try:
            sp.user_follow_artists(batch)
            followed_count += len(batch)
            print(f"  -> Followed a batch of {len(batch)} artists.")
        except Exception as e:
            print(f"  -> Could not follow a batch. Error: {e}")
    
    print(f"\n✅ Successfully followed {followed_count} artists.")

if __name__ == '__main__':
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        print("🛑 ERROR: Make sure CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI are set in your .env file.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python follow_artists.py <spotify_playlist_url>")
        sys.exit(1)

    # Authenticate with user permission
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=REDIRECT_URI,
                                scope=SCOPE)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    playlist_link = sys.argv[1]
    
    # Get currently followed artists to avoid re-following (optional but good practice)
    # Note: This part is omitted for simplicity, as the follow API doesn't error on duplicates.
    
    artist_ids_to_follow = get_unique_artist_ids(sp, playlist_link)
    
    if artist_ids_to_follow:
        follow_artists_in_batches(sp, artist_ids_to_follow)
        print("\n🎉 All tasks complete.")
