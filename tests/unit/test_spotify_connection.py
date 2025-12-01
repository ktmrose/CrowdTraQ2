import pytest, time, urllib.parse
from unittest.mock import patch, MagicMock
import app.core.spotify_client as spotify_client
from app.config.settings import HOST

# --- Constructor defaults ---

def test_spotify_connection_initial_state(monkeypatch):
    monkeypatch.setattr(spotify_client, "SPOTIFY_CLIENT_ID", "abc123")
    monkeypatch.setattr(spotify_client, "SPOTIFY_CLIENT_SECRET", "secret456")

    conn = spotify_client.SpotifyConnection()
    assert conn._spotify_general_token is None
    assert conn._spotify_user_token is None
    assert conn._spotify_refresh_token is None
    assert conn._token_expiration == 0
    assert conn._client_id == "abc123"
    assert conn._client_secret == "secret456"

# --- Authorization URL ---

def test_get_authorization_url_contains_client_id(monkeypatch):
    monkeypatch.setattr(spotify_client, "SPOTIFY_CLIENT_ID", "abc123")
    monkeypatch.setattr(spotify_client, "SPOTIFY_CLIENT_SECRET", "secret456")

    conn = spotify_client.SpotifyConnection()
    url = conn.get_authorization_url()
    assert "client_id=abc123" in url
    assert "response_type=code" in url
    expected_redirect = urllib.parse.urlencode(
        {"redirect_uri": f"http://{HOST}:8081/callback"}
    )
    assert expected_redirect in url


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

    conn = spotify_client.SpotifyConnection()
    conn.exchange_code_for_token("fake-code")

    assert conn._spotify_user_token == "user123"
    assert conn._spotify_refresh_token == "refresh123"
    assert conn._token_expiration > time.time()

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

    conn = spotify_client.SpotifyConnection()
    conn._spotify_refresh_token = "oldrefresh"
    conn.refresh_access_token()

    assert conn._spotify_user_token == "newtoken"
    assert conn._spotify_refresh_token == "newrefresh"
    assert conn._token_expiration > time.time()

# --- Ensure token valid ---

@patch.object(spotify_client.SpotifyConnection, "refresh_access_token")
def test_ensure_token_valid_triggers_refresh(mock_refresh):
    conn = spotify_client.SpotifyConnection()
    conn._spotify_user_token = None
    conn._token_expiration = 0

    conn.ensure_token_valid()
    mock_refresh.assert_called_once()