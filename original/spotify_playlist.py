import requests
import json
from googleapiclient.discovery import build

#class definition for creating a playlist and initializing attributes for the class
class CreatePlaylist:
    def __init__(self):
        self.client_id = "65e4d985b21645ab9eb6cff676e17655"  #client ID from Spotify
        self.client_secret = "2f41919cbfb248539a8db2330d364457"  #client secret from Spotify
        self.spotify_token = self.get_token()                    # Get Spotify access token
        self.playlistId = "PLFMamqa_6wIhfNaOxGyQztvPQgAGwgLo6"  #playlist ID
        self.user_id = "Gp2DdP5FEa_EDy4jzMBvRQ"                 #User ID related to the playlist
        self.yt_song_list = []                     #list to store YouTube video titles
        self.uri_list = []                         #list to store uri Spotify tracks
        self.uri_dict = {}                         #dictionary that maps YouTube video titles to Spotify URIs

#function to get access token
    def get_token(self):
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        auth_response_data = auth_response.json()
        token = auth_response_data['access_token']
        return token

#get YouTube songs from the "H.E.R" playlist
    def get_youtube_songs(self):
         # API key for accessing YouTube Data API
        yt_api_key = "AIzaSyBKn9jXWi-zZ0HZjVdu5rkPPDa1HhkLYzg"

        #service object for interacting with YouTube Data API
        youtube_constructor = build("youtube", "v3", developerKey=yt_api_key)

        # Request to get playlist items (videos) from the YT playlist
        results = youtube_constructor.playlistItems().list(
            playlistId=self.playlistId,
            part="snippet",
            maxResults=20
        ).execute()
        amount_songs = results["pageInfo"]["totalResults"]

        #loop through the items (videos) retrieved from the playlist
        for item in results["items"]:
            self.yt_song_list.append(item["snippet"]["title"])
        print(self.yt_song_list)

#search for songs on Spotify and retrieve their URIs
    def search_songs_spotify(self):

        self.get_youtube_songs() #call the get_youtube_songs function to get YT video titles

       #iterate over each YT video title in yt_song_list 
        for title in self.yt_song_list:
            search_query = "https://api.spotify.com/v1/search?query=track%3A{}&type=track&offset=0&limit=1".format(title) #Spotify search query URL for the current YT video title
            
            json_response = requests.get(  #initiate a GET request to the Spotify API to search for the track
            search_query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
            
        #print the response for each song search on Spotify    
        print("Response for each song search on Spotify:", json_response)
        response = json_response.json()
        
        self.uri_dict["uris"] = self.uri_list #store the list of URIs in uri_dict under the key "uris"
        return self.uri_dict #return the dictionary containing the URIs

#create new playlist on Spotify
    def create_new_playlist(self):

        #Spotify API endpoint URL to create a new playlist
        blank_query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)

        requests_body = json.dumps(     #dictionary containing details of new playlist
        {
            "name": "H.E.R Playlist",
            "description": "Best of H.E.R",
            "public": True
        }
    )

     #send a POST request to the Spotify API to create the new playlist   
        json_response = requests.post(
        blank_query,
        data=requests_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.spotify_token)
        }
    )
        
         #print the response for new playlist creation on Spotify
        print("Response for new playlist creation on Spotify:", json_response)
    
        response = json_response.json()
        print("Response JSON:", response)  # Print the response JSON for debugging purposes
    
        new_playlist_id = response.get("id")  # Use .get() method to avoid KeyError if 'id' key is missing

        return new_playlist_id  #return the ID of the new playlist

#adding songs to the new playlist
    def add_songs_new_playlist(self):

        self.search_songs_spotify()  #get the songs on Spotify and retrieve their URIs

        create_new = self.create_new_playlist() #create a new playlist on Spotify and get its ID

      #construct the Spotify API endpoint URL to add tracks to the newly created playlist  
        add_query = "https://api.spotify.com/v1/playlists/{}/tracks".format(create_new)

        #convert the dictionary containing URIs to JSON format
        request_data = json.dumps(self.uri_dict)

        json_response = requests.post(   #POST request to add tracks to the new playlist
            add_query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )

        # Print the response for adding songs to the new playlist on Spotify
        print("Response for adding songs to new playlist on Spotify:", json_response)

obj = CreatePlaylist()
obj.add_songs_new_playlist()


