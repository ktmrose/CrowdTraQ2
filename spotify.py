import base64
import os
import time
import requests
import urllib.parse
from config import api, request_info

class SpotifyConnection:
    def __init__(self):
        self.spotify_general_token = None
        self.spotify_user_token = None
        self.spotify_refresh_token = None
        self.client_id = os.getenv("spotify_client_id")
        self.client_secret = os.getenv("spotify_client_secret")
        self.token_expiration = 0

    # used for calls that do not require user permissions (i.e. song lookup)
    def initialize_general_access_token(self):
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode(),
            "Content-Type": request_info["content_type"]
        }
        data = {
            "grant_type": "client_credentials"
        }
        response = requests.post(api["token"], headers=headers, data=data)
        self.spotify_general_token = response.json()

    def get_authorization_url(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost:8081/callback",
            "scope": "user-modify-playback-state user-read-currently-playing user-read-playback-state",
        }
        authorize_url = f"{api["authorize"]}?{urllib.parse.urlencode(params)}"
        return authorize_url
    
    def exchange_code_for_token(self, authorization_code):
        headers = {
            "Content-Type": request_info["content_type"]
        }
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "http://localhost:8081/callback",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(api["token"], headers=headers, data=data)
        token_info = response.json()
        self.spotify_user_token = token_info["access_token"]
        self.spotify_refresh_token = token_info["refresh_token"]
        expires_in = token_info["expires_in"] # 3600 seconds
        self.token_expiration = time.time() + expires_in - 60  # refresh 1 min early
        print("Spotify user token expires at: ", self.token_expiration)

    def refresh_access_token(self):
        headers = {
            "Content-Type": request_info["content_type"]
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.spotify_refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        print("getting refresh token...")
        response = requests.post(api["token"], headers=headers, data=data)
        token_info = response.json()
        self.access_token = token_info["access_token"]
        expires_in = token_info.get("expires_in", 3600)
        self.token_expiration = time.time() + expires_in - 60  # refresh 1 min early

    def ensure_token_valid(self):
        if self.spotify_user_token is None or self.token_expiration <= time.time():
            self.refresh_access_token()
    
    def get_currently_playing(self):
        self.ensure_token_valid()
        headers = {
            "Authorization": f"Bearer {self.spotify_user_token}"
        }
        response = requests.get(api["currently_playing"], headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            print("No track currently playing.")
            return None
        else:
            raise Exception(f"Error getting currently playing track: {response.status_code} - {response.text}")
        
    def search_songs(self, query, type="track", limit=5):
        headers = {
            "Authorization": f"Bearer {self.spotify_user_token}"
        }
        params = {
            "q": query,
            "type": type,
            "limit": limit
        }
        response = requests.get(api["track_search"], headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Unauthorized request. Refreshing token...")
            self.refresh_access_token()
            return self.search_songs(query, type, limit)
        else:
            raise Exception(f"Error searching for songs: {response.status_code} - {response.text}")
        
    def add_track_by_id(self, track_id):
        self.ensure_token_valid()
        headers = {
            "Authorization": f"Bearer {self.spotify_user_token}",
            "Content-Type": "application/json"
        }
        params = {
            "uri": f"spotify:track:{track_id}"
        }
        response = requests.post(api["add_to_queue"], headers=headers, params=params)
        return response