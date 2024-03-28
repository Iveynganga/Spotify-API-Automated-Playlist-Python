import json
import requests
import os
from cred import spotify_user_id
from cred import spotify_token
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl


class CreatePlaylist:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    #Start by logging into YouTube

    def get_youtube_client(self):
        #copied from YouTube Data API
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "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"
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
        credentials = flow.run_console()

    #from YouTube Data API
        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

        return youtube_client
    

#Go to HER playlist
    def get_her_playlist(self, playlist_id):
        request = self.youtube_client.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        playlist_id = 'PLFMamqa_6wIhfNaOxGyQztvPQgAGwgLo6',
        maxResults=20  
    )
        response = requests.execute()

        # Collect each video and get important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url="https://www.youtube.com/watch?v={}".format(item["id"])

            # Use YouTube DL to collect the song name and artist name
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video.get("track")
            artist = video.get("artist")

            # Save all these details
            self.all_song_info[video_title] = {
                "youtube_url": youtube_url,
                "song_name": song_name,
                "artist": artist,

                # Add the uri to make it easy to get song to put into playlist
                "spotify_uri": self.get_spotify_uri(song_name, artist)
            }

#Create the playlist on Spotify
    def create_playlist(self):

        request_body = json.dumps({
    "name": "H.E.R YouTube Playlist",
    "description": "H.E.R Playlist",
    "public": True
        })

        query = "https://api.spotify.com/v1/users/{user_id}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data = request_body,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer{}".format(spotify_token) #send out this request
            }
        )
        response_json = response.json() #sieve the playlist Id

            #playlist id
        return response_json("id")

#search for the song
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

#add the song to new Spotify playlist
    def add_playlist_(self):
        #populate the songs dictionary
        self.get_her_playlist()

        #collect all of uri
        uris = []
        for song,info in self.all_song_info.items():
            uris.append(info["spotify_uri"])

        #create a new playlist
            playlist_id =self.create_playlist()

        #add all songs into new playlist
            request_data = json.dumps(uris)

            query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
            
            response = requests.post(
                query,
                data=requests.data,
                headers = {
                    "Content-Type":"application/json",
                    "Authorization":"Bearer{}".format(self.spotify_token)
                }
            )
            response_json = response.json()
            return response_json

playlist_creator = CreatePlaylist()
print(playlist_creator)