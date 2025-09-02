# spotify scripts 

A collection of simple spotify scripts to extend functionallity

## Usage

1. Create a python virtual env

```
python3 -m venv venv
```

2. Activate the venv
 
```
./venv/bin/activate
```

3. Install dependencies

```
pip install python-dotenv spotipy
```

4. Install yt-dlp (optional for downloader)

```
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

or use the package manager of your choice

5. Get credentials for spotify

Go to the [Spotify developer dashboard](https://developer.spotify.com/dashboard/) and create a client id and secret and paste it into the [.env file](./.env).

6. Start downloading

```
python <script>.py 'YOUR_SPOTIFY_PLAYLIST_URL'
```
