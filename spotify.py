import base64
import os
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
            "scope": "user-modify-playback-state",
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

    def refresh_access_token(self):
        headers = {
            "Content-Type": request_info["content_type"]
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        print("getting refresh token")
        response = requests.post(api["token"], headers=headers, data=data)
        token_info = response.json()
        self.access_token = token_info["access_token"]
    
    def get_currently_playing(self):
        headers = {
            "Authorization": f"Bearer {self.spotify_user_token}"
        }
        response = requests.get(api["currently_playing"], headers=headers)
        print(response.json())