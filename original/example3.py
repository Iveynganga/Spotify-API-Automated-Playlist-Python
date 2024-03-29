import requests
import os
import json 
from cred import spotify_user_id, spotify_token
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class CreatePlaylist:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        

    # log into YouTube
    def get_youtube_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret_832550295475-num4d637a4n5o2qgg2ppu2ds8jc9co1o.apps.googleusercontent.com.json"
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        credentials = flow.run_console()
        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
        return youtube_client
    
    # Create a Spotify playlist
    def create_her_playlist(self):
        request_body = {
            "name": "H.E.R YouTube Playlist",
            "description": "H.E.R Playlist",
            "public": True
        }
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=json.dumps(request_body),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        # Return the playlist ID
        return response_json["id"]

    def create_spotify_uri(self, song_name, artist):
        
        query = "https://api.spotify.com/v1/me/shows?offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer{}".format(self.spotify_token) #send out this request
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri

    # Get the artist information
    def get_artist_info(self, artist_name):
        headers = {
            "Authorization": "Bearer " + self.spotify_token
        }
        params = {
            "q": artist_name,
            "type": "artist"
        }
        response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['artists']['items']:
                artist_info = data['artists']['items'][0]
                return artist_info
        return None


playlist_creator = CreatePlaylist()
playlist_creator.create_playlist()

