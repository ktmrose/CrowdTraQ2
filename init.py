from string import ascii_uppercase
from random import choice
from spotify_manager import SpotifyConnectionManager
from flask import Flask
from werkzeug.serving import make_server
from threading import Thread
from routes import register_routes

app = Flask(__name__)

register_routes(app)

class SpotifyConnectionThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.server = make_server('localhost', 8081, app)
        self.context = app.app_context()
        self.context.push()
    
    def run(self):
        print("Starting Spotify integration thread...")
        self.server.serve_forever()
    
    def shutdown(self):
        print("Shutting down Spotify integration thread...")
        self.server.shutdown()

def generate_room_code(length):
    room_code = ''
    for i in range(length):
        room_code = room_code + choice(ascii_uppercase)
    return room_code

def start_spotify_client():
    spotify_client_thread = SpotifyConnectionThread()
    spotify_client_thread.start()
    return spotify_client_thread

def establish_spotify_connection():
    spotify_connection = SpotifyConnectionManager().get_instance()
    # spotify_connection.initialize_general_access_token()
    # print(spotify_connection.spotify_general_token)
    print("Go to this URL to authorize your app:", spotify_connection.get_authorization_url())