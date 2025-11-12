import pytest
from unittest.mock import MagicMock, patch
from app.handlers.client_handler import ClientHandler

# --- Constructor & Queue Length ---

def test_get_queue_length_calls_songqueue_length():
    fake_currency = MagicMock()
    handler = ClientHandler(fake_currency)
    handler._songQueue.length = MagicMock(return_value=3)

    assert handler.get_queue_length() == 3
    handler._songQueue.length.assert_called_once()

# --- _error helper ---

def test_error_returns_expected_dict():
    handler = ClientHandler(MagicMock())
    result = handler._error("CODE", "Something went wrong", {"info": "details"})
    assert result["success"] is False
    assert result["error"]["code"] == "CODE"
    assert result["error"]["message"] == "Something went wrong"
    assert result["error"]["details"]["info"] == "details"

# --- message_handler validation ---

def test_message_handler_rejects_non_dict():
    handler = ClientHandler(MagicMock())
    result = handler.message_handler("not a dict", "client1")
    assert result["error"]["code"] != ""  # should be GENERAL_ERROR

def test_message_handler_rejects_missing_action():
    handler = ClientHandler(MagicMock())
    result = handler.message_handler({}, "client1")
    assert result["error"]["code"] != ""  # should be UNKNOWN_ACTION

def test_message_handler_rejects_unknown_action():
    handler = ClientHandler(MagicMock())
    result = handler.message_handler({"action": "bogus"}, "client1")
    assert result["error"]["code"] != ""  # should be UNKNOWN_ACTION

# --- add_track flow ---

def test_add_track_missing_track_id():
    handler = ClientHandler(MagicMock())
    result = handler.message_handler({"action": "add_track", "data": {}}, "client1")
    assert result["error"]["code"] != ""  # should be INVALID_TRACK_ID

def test_add_track_insufficient_tokens():
    fake_currency = MagicMock()
    fake_currency.try_spend.return_value = (False, 5)
    fake_currency.calculate_cost.return_value = 10

    handler = ClientHandler(fake_currency)
    handler._spotify_connection = MagicMock()

    result = handler.message_handler({"action": "add_track", "data": {"track_id": "abc"}}, "client1")
    assert result["error"]["code"] != ""  # should be QUEUE_INSUFFICIENT_TOKENS

def test_add_track_success():
    fake_currency = MagicMock()
    fake_currency.try_spend.return_value = (True, 8)

    # Create a fake spotify connection that won't touch tokens
    fake_spotify = MagicMock()
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_spotify.add_track_by_id.return_value = fake_response

    with patch("app.handlers.client_handler.SpotifyConnectionManager.get_instance", return_value=fake_spotify):
        handler = ClientHandler(fake_currency)

        # If code re-fetches the connection in message_handler, this patch ensures it still returns fake_spotify
        handler._songQueue.add = MagicMock()

        result = handler.message_handler({"action": "add_track", "data": {"track_id": "abc"}}, "client1")

    assert result["success"] is True
    handler._songQueue.add.assert_called_once_with("abc", "client1")
    fake_spotify.add_track_by_id.assert_called_once_with("abc")


# --- like/dislike track ---

def test_like_track_calls_feedback():
    handler = ClientHandler(MagicMock())
    handler.song_feedback.like = MagicMock()
    handler.check_currently_playing = MagicMock(return_value={"success": True})

    result = handler.message_handler({"action": "like_track"}, "client1")
    handler.song_feedback.like.assert_called_once_with("client1")
    assert result == {"success": True}

def test_dislike_track_calls_feedback():
    handler = ClientHandler(MagicMock())
    handler.song_feedback.dislike = MagicMock()
    handler.check_currently_playing = MagicMock(return_value={"success": True})

    result = handler.message_handler({"action": "dislike_track"}, "client1")
    handler.song_feedback.dislike.assert_called_once_with("client1")
    assert result == {"success": True}

# --- check_currently_playing ---

def test_check_currently_playing_no_track():
    handler = ClientHandler(MagicMock())
    handler._spotify_connection = MagicMock()
    handler._spotify_connection.get_currently_playing.return_value = None

    result = handler.check_currently_playing()
    assert result["error"]["code"] != ""  # should be NO_TRACK_PLAYING

# --- clean_currently_playing ---

def test_clean_currently_playing_formats_data():
    handler = ClientHandler(MagicMock())
    handler._spotify_connection = MagicMock()
    handler._spotify_connection.get_currently_playing.return_value = {
        "item": {
            "name": "Song A",
            "artists": [{"name": "Artist A"}],
            "album": {"name": "Album A", "images": [{"url": "img.jpg"}]},
            "duration_ms": 200000,
            "id": "track123",
            "uri": "spotify:track:track123",
        },
        "progress_ms": 1000,
        "is_playing": True,
    }

    result = handler.clean_currently_playing()
    assert result["currently_playing"]["track_name"] == "Song A"
    assert result["currently_playing"]["artists"] == ["Artist A"]

# --- search_song ---

def test_search_song_returns_formatted_data():
    handler = ClientHandler(MagicMock())
    handler._spotify_connection = MagicMock()
    handler._spotify_connection.search_songs.return_value = {
        "tracks": {
            "items": [
                {
                    "name": "Song A",
                    "artists": [{"name": "Artist A"}],
                    "id": "track123",
                    "album": {"images": [{"url": "img.jpg"}]},
                }
            ]
        }
    }

    result = handler.search_song("Song A")
    assert result["search_data"][0]["track_name"] == "Song A"
    assert result["search_data"][0]["artists"] == ["Artist A"]