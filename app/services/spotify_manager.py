from app.core.spotify_client import SpotifyConnection

class SpotifyConnectionManager:
    _instance = None

    @staticmethod
    def get_instance():
        if SpotifyConnectionManager._instance is None:
            SpotifyConnectionManager._instance = SpotifyConnection()
        return SpotifyConnectionManager._instance