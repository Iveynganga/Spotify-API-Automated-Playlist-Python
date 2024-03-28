import json
import requests
import os
from cred import spotify_user_id, spotify_token
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

class CreatePlaylist:
    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    def get_youtube_client(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json')
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credj.json', ['https://www.googleapis.com/auth/youtube.readonly'])
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        youtube_client = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
        return youtube_client

    def get_liked_videos(self):
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )
        response = request.execute()
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video.get("track")
            artist = video.get("artist")
            self.all_song_info[video_title] = {
                "youtube_url": youtube_url,
                "song_name": song_name,
                "artist": artist,
                "spotify_uri": self.create_spotify_uri(song_name, artist)
            }

    def create_playlist(self):
        request_body = json.dumps({
            "name": "YouTube Liked Vids",
            "description": "All Liked YouTube Videos",
            "public": True
        })
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        return response_json["id"]

    def create_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?q=track:{}%20artist:{}&type=track".format(song_name, artist)
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        uri = response_json["tracks"]["items"][0]["uri"]
        return uri

    def add_playlist(self):
        self.get_liked_videos()
        uris = [info["spotify_uri"] for song, info in self.all_song_info.items()]
        playlist_id = self.create_playlist()
        request_data = json.dumps({"uris": uris})
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        return response_json

playlist_creator = CreatePlaylist()
print(playlist_creator.add_playlist())
