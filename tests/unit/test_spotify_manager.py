import pytest
from unittest.mock import patch, MagicMock
from app.services.spotify_manager import SpotifyConnectionManager

def teardown_function():
    # Reset singleton between tests
    SpotifyConnectionManager._instance = None

@patch("app.services.spotify_manager.SpotifyConnection", autospec=True)
def test_get_instance_creates_new_connection(mock_conn):
    mock_conn.return_value = MagicMock()
    SpotifyConnectionManager._instance = None  # reset singleton
    inst = SpotifyConnectionManager.get_instance()
    assert inst is mock_conn.return_value

def test_get_instance_returns_same_instance():
    with patch("app.services.spotify_manager.SpotifyConnection", autospec=True) as mock_conn:
        mock_conn.return_value = MagicMock()
        inst1 = SpotifyConnectionManager.get_instance()
        inst2 = SpotifyConnectionManager.get_instance()
        # Should not call SpotifyConnection again
        mock_conn.assert_called_once()
        assert inst1 is inst2

def test_get_instance_without_patch_returns_real_object():
    # This just ensures it doesn't crash if we let it construct a real SpotifyConnection
    # Reset first
    SpotifyConnectionManager._instance = None
    inst = SpotifyConnectionManager.get_instance()
    assert inst is SpotifyConnectionManager._instance