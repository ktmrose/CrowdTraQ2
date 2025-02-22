import base64
import requests

client_id = '527edd7fd9f84312adbbb2dbc4824e0c'
client_secret = '0b92968afe9340c3821dce07b142a3a9'

def get_access_token():
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
