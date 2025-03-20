import base64
import os
import requests

class SpotifyConnection:
    def __init__(self):
        self.spotify_token = None
        self.client_id = os.getenv("spotify_client_id")
        self.client_secret = os.getenv("spotify_client_secret")

    def initialize_access_token(self):
        token_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }
        response = requests.post(token_url, headers=headers, data=data)
        self.spotify_token = response.json()

    def get_access_token(self):
        return self.spotify_token