import pytest
from handlers import clean_currently_playing, user_search_songs, handle_user_message

@pytest.fixture
def mock_spotify_connection(monkeypatch):
    class MockSpotify:
        def search_songs(self, query, type="track", limit=10):
            return {
                "tracks": {
                    "items": [
                        {"name": "Song1", "artists": [{"name": "Artist1"}], "album": {"name": "Album1", "images": [{"url": "img1"}]}, "duration_ms": 1000, "id": "id1", "uri": "uri1"},
                        {"name": "Song2", "artists": [{"name": "Artist2"}], "album": {"name": "Album2", "images": [{"url": "img2"}]}, "duration_ms": 2000, "id": "id2", "uri": "uri2"},
                    ]
                }
            }
    return MockSpotify()

def test_clean_currently_playing():
    response = {
        "item": {
            "name": "Test Song",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album", "images": [{"url": "test_url"}]},
            "duration_ms": 12345,
            "id": "trackid",
            "uri": "spotify:track:trackid"
        },
        "progress_ms": 1000,
        "is_playing": True
    }
    result = clean_currently_playing(response)
    assert result["track_name"] == "Test Song"
    assert result["artists"] == ["Test Artist"]
    assert result["album"] == "Test Album"
    assert result["album_art"] == "test_url"
    assert result["duration_ms"] == 12345
    assert result["progress_ms"] == 1000
    assert result["is_playing"] is True
    assert result["track_id"] == "trackid"
    assert result["uri"] == "spotify:track:trackid"

def test_user_search_songs(mock_spotify_connection):
    results = user_search_songs(mock_spotify_connection, "test")
    assert len(results) == 2
    assert results[0]["name"] == "Song1"
    assert results[1]["name"] == "Song2"

def test_handle_user_message_search(mock_spotify_connection):
    message = "search:test"
    response = handle_user_message(message, mock_spotify_connection)
    assert response["type"] == "search_results"
    assert len(response["results"]) == 2

def test_handle_user_message_other(mock_spotify_connection):
    message = "other:message"
    response = handle_user_message(message, mock_spotify_connection)
    assert response is None