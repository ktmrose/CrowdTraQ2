import base64
import os
import requests

client_id = os.getenv("spotify_client_id")
client_secret = os.getenv("spotify_client_secret")

spotify_access_token = None
token_expiry_time = None

def initialize_access_token():
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(token_url, headers=headers, data=data)
    token_info = response.json()
    access_token = token_info["access_token"]
    return access_token

def get_access_token():
    spotify_access_token = initialize_access_token()
    return spotify_access_token