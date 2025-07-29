from spotify_manager import SpotifyConnectionManager

def test_singleton():
    inst1 = SpotifyConnectionManager.get_instance()
    inst2 = SpotifyConnectionManager.get_instance()
    assert inst1 is inst2