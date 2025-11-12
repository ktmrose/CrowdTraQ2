import pytest
import time
from unittest.mock import patch, MagicMock
from app.core.spotify_client import SpotifyConnection

# --- Constructor defaults ---

def test_spotify_connection_initial_state(monkeypatch):
    monkeypatch.setenv("spotify_client_id", "abc123")
    monkeypatch.setenv("spotify_client_secret", "secret456")

    conn = SpotifyConnection()
    assert conn.spotify_general_token is None
    assert conn.spotify_user_token is None
    assert conn.spotify_refresh_token is None
    assert conn.token_expiration == 0
    assert conn.client_id == "abc123"
    assert conn.client_secret == "secret456"

# --- Authorization URL ---

def test_get_authorization_url_contains_client_id(monkeypatch):
    monkeypatch.setenv("spotify_client_id", "abc123")
    monkeypatch.setenv("spotify_client_secret", "secret456")

    conn = SpotifyConnection()
    url = conn.get_authorization_url()
    assert "client_id=abc123" in url
    assert "response_type=code" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8081%2Fcallback" in url

# --- Token exchange ---

@patch("app.core.spotify_client.requests.post")
def test_exchange_code_for_token_sets_tokens(mock_post, monkeypatch):
    monkeypatch.setenv("spotify_client_id", "abc123")
    monkeypatch.setenv("spotify_client_secret", "secret456")

    fake_response = MagicMock()
    fake_response.json.return_value = {
        "access_token": "user123",
        "refresh_token": "refresh123",
        "expires_in": 3600,
    }
    mock_post.return_value = fake_response

    conn = SpotifyConnection()
    conn.exchange_code_for_token("fake-code")

    assert conn.spotify_user_token == "user123"
    assert conn.spotify_refresh_token == "refresh123"
    assert conn.token_expiration > time.time()

# --- Refresh token ---

@patch("app.core.spotify_client.requests.post")
def test_refresh_access_token_updates_tokens(mock_post, monkeypatch):
    monkeypatch.setenv("spotify_client_id", "abc123")
    monkeypatch.setenv("spotify_client_secret", "secret456")

    fake_response = MagicMock()
    fake_response.json.return_value = {
        "access_token": "newtoken",
        "refresh_token": "newrefresh",
        "expires_in": 1800,
    }
    mock_post.return_value = fake_response

    conn = SpotifyConnection()
    conn.spotify_refresh_token = "oldrefresh"
    conn.refresh_access_token()

    assert conn.spotify_user_token == "newtoken"
    assert conn.spotify_refresh_token == "newrefresh"
    assert conn.token_expiration > time.time()

# --- Ensure token valid ---

@patch.object(SpotifyConnection, "refresh_access_token")
def test_ensure_token_valid_triggers_refresh(mock_refresh):
    conn = SpotifyConnection()
    conn.spotify_user_token = None
    conn.token_expiration = 0

    conn.ensure_token_valid()
    mock_refresh.assert_called_once()