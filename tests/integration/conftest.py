import pytest
from unittest.mock import MagicMock
from app.services.currency_manager import CurrencyManager
from app.services.queue_manager import SongQueue, SongFeedback
from app.services.identity_manager import IdentityManager
from app.services.playback_manager import PlaybackManager

@pytest.fixture
def currency_manager():
    return CurrencyManager()

@pytest.fixture
def song_queue():
    return SongQueue()

@pytest.fixture
def song_feedback():
    return SongFeedback()

@pytest.fixture
def identity_manager():
    return IdentityManager()

@pytest.fixture
def fake_spotify(monkeypatch):
    class FakeResponse:
        def __init__(self, status_code=200):
            self.status_code = status_code

    fake_conn = MagicMock()
    fake_conn.add_track_by_id.return_value = FakeResponse(200)
    fake_conn.get_currently_playing.return_value = {
        "item": {"id": "t999", "name": "Fake Track", "artists": [{"name": "Artist"}], "album": {"name": "Album", "images": [{"url": "http://fake"}]}},
        "progress_ms": 100,
        "is_playing": True,
    }
    fake_conn.search_songs.return_value = {"tracks": {"items": [{"id": "t123", "name": "Fake Track", "artists": [{"name": "Artist"}], "album": {"images": [{"url": "http://fake"}]}}]}}
    monkeypatch.setattr("app.handlers.client_handler.SpotifyConnectionManager.get_instance", lambda: fake_conn)
    return fake_conn


@pytest.fixture
def playback_manager(currency_manager, song_queue, song_feedback, fake_spotify):
    return PlaybackManager(fake_spotify, song_queue, song_feedback, currency_manager)
