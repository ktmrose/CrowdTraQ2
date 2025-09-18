import pytest
from app.core.spotify_client import SpotifyConnection

@pytest.fixture
def spotify(monkeypatch):
    conn = SpotifyConnection()
    conn.client_id = "test_id"
    conn.client_secret = "test_secret"
    conn.spotify_user_token = "test_token"
    return conn

def test_get_authorization_url(spotify):
    url = spotify.get_authorization_url()
    assert "client_id=test_id" in url

def test_search_songs(monkeypatch, spotify):
    def mock_get(url, headers, params):
        class MockResponse:
            status_code = 200
            def json(self):
                return {"tracks": {"items": [{"name": "Test Song"}]}}
        return MockResponse()
    monkeypatch.setattr("requests.get", mock_get)
    result = spotify.search_songs("test")
    assert "tracks" in result
    assert result["tracks"]["items"][0]["name"] == "Test Song"