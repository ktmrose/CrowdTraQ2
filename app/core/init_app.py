from string import ascii_uppercase
from random import choice
from app.services.spotify_manager import SpotifyConnectionManager
from flask import Flask
from werkzeug.serving import make_server
from threading import Thread
from app.routes.routes import register_routes
import logging

logger = logging.getLogger("app.core.init_app")

app = Flask(__name__)
register_routes(app)

class SpotifyConnectionThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.server = make_server('localhost', 8081, app)
        self.context = app.app_context()
        self.context.push()
    
    def run(self):
        logger.debug("Starting Spotify integration thread...")
        self.server.serve_forever(poll_interval=0.1)
        logger.debug("Spotify integration thread exiting...")
    
    def shutdown(self):
        logger.debug("Shutting down Spotify integration thread...")
        self.server.shutdown()

def generate_room_code(length):
    room_code = ''
    for i in range(length):
        room_code = room_code + choice(ascii_uppercase)
    return room_code

def start_spotify_integration():
    """
    Start Flask server (always) and Spotify client thread (only if tokens exist).
    Returns a tuple (flask_thread, spotify_client_thread).
    """
    # Start Flask server for /callback
    flask_thread = SpotifyConnectionThread()
    flask_thread.start()

    conn = SpotifyConnectionManager.get_instance()
    if not conn.load_tokens():
        logger.info("No tokens.json found. Run admin.py authorize to complete Spotify setup.")
        return flask_thread, None

    # Start Spotify client thread if tokens are loaded
    spotify_client_thread = SpotifyConnectionThread()
    spotify_client_thread.start()

    return flask_thread, spotify_client_thread

def establish_spotify_connection():
    spotify_connection = SpotifyConnectionManager.get_instance()
    auth_url = spotify_connection.get_authorization_url()
    logger.debug("Authorization URL generated: %s", auth_url)
    return auth_url