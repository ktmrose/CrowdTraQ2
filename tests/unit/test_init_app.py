import pytest
from unittest.mock import patch, MagicMock
import string

from app.core.init_app import (
    SpotifyConnectionThread,
    generate_room_code,
    start_spotify_client,
    establish_spotify_connection,
)

# --- SpotifyConnectionThread ---

@patch("app.core.init_app.make_server")
def test_spotify_thread_init_sets_server(mock_make_server):
    mock_server = MagicMock()
    mock_make_server.return_value = mock_server

    thread = SpotifyConnectionThread()
    assert thread.server is mock_server
    assert thread.context is not None

def test_spotify_thread_shutdown_calls_server_shutdown():
    thread = SpotifyConnectionThread()
    thread.server = MagicMock()
    thread.shutdown()
    thread.server.shutdown.assert_called_once()

# --- generate_room_code ---

def test_generate_room_code_length():
    code = generate_room_code(6)
    assert len(code) == 6

def test_generate_room_code_uppercase_only():
    code = generate_room_code(10)
    assert all(c in string.ascii_uppercase for c in code)

# --- start_spotify_client ---

@patch("app.core.init_app.SpotifyConnectionThread")
def test_start_spotify_client_starts_thread(mock_thread_cls):
    mock_thread = MagicMock()
    mock_thread_cls.return_value = mock_thread

    result = start_spotify_client()
    mock_thread.start.assert_called_once()
    assert result is mock_thread

# --- establish_spotify_connection ---

@patch("app.core.init_app.SpotifyConnectionManager")
def test_establish_spotify_connection_calls_get_url(mock_mgr_cls):
    mock_mgr_instance = MagicMock()
    mock_mgr_instance.get_authorization_url.return_value = "http://fake-url"

    # Make get_instance return the mock instance
    mock_mgr_cls.return_value.get_instance.return_value = mock_mgr_instance

    establish_spotify_connection()
    mock_mgr_instance.get_authorization_url.assert_called_once()
