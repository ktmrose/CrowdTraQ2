import pytest
from unittest.mock import patch, MagicMock
import string

from app.core.init_app import (
    SpotifyConnectionThread,
    generate_room_code,
    start_spotify_integration,
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

# --- start_spotify_integration ---

@patch("app.core.init_app.SpotifyConnectionThread")
@patch("app.core.init_app.SpotifyConnectionManager")
def test_start_spotify_integration_no_tokens(mock_mgr_cls, mock_thread_cls):
    mock_thread = MagicMock()
    mock_thread_cls.return_value = mock_thread

    mock_mgr_instance = MagicMock()
    mock_mgr_instance.load_tokens.return_value = False
    mock_mgr_cls.get_instance.return_value = mock_mgr_instance

    flask_thread, spotify_client_thread = start_spotify_integration()

    mock_thread.start.assert_called_once()
    assert flask_thread is mock_thread
    assert spotify_client_thread is None

@patch("app.core.init_app.SpotifyConnectionThread")
@patch("app.core.init_app.SpotifyConnectionManager")
def test_start_spotify_integration_with_tokens(mock_mgr_cls, mock_thread_cls):
    mock_flask_thread = MagicMock()
    mock_client_thread = MagicMock()
    mock_thread_cls.side_effect = [mock_flask_thread, mock_client_thread]

    mock_mgr_instance = MagicMock()
    mock_mgr_instance.load_tokens.return_value = True
    mock_mgr_cls.get_instance.return_value = mock_mgr_instance

    flask_thread, spotify_client_thread = start_spotify_integration()

    assert mock_flask_thread.start.called
    assert mock_client_thread.start.called
    assert flask_thread is mock_flask_thread
    assert spotify_client_thread is mock_client_thread

# --- establish_spotify_connection ---

@patch("app.core.init_app.SpotifyConnectionManager")
def test_establish_spotify_connection_calls_get_url(mock_mgr_cls):
    mock_mgr_instance = MagicMock()
    mock_mgr_instance.get_authorization_url.return_value = "http://fake-url"
    mock_mgr_cls.get_instance.return_value = mock_mgr_instance

    url = establish_spotify_connection()
    mock_mgr_instance.get_authorization_url.assert_called_once()
    assert url == "http://fake-url"