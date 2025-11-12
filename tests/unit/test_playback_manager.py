import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.playback_manager import PlaybackManager

@pytest.fixture
def setup_manager():
    spotify = MagicMock()
    queue = MagicMock()
    feedback = MagicMock()
    currency = MagicMock()
    manager = PlaybackManager(spotify, queue, feedback, currency)
    return manager, spotify, queue, feedback, currency

def test_get_current_track_id_returns_none(setup_manager):
    manager, *_ = setup_manager
    assert manager._get_current_track_id({}) is None
    assert manager._get_current_track_id({"is_playing": False}) is None

def test_get_current_track_id_returns_id(setup_manager):
    manager, *_ = setup_manager
    info = {"is_playing": True, "item": {"id": "track123"}}
    assert manager._get_current_track_id(info) == "track123"

def test_calculate_sleep_time_basic(setup_manager):
    manager, *_ = setup_manager
    info = {"item": {"duration_ms": 10000}, "progress_ms": 2000}
    sleep = manager._calculate_sleep_time(info)
    # (10000-2000)/1000 - 1 = 7.0
    assert abs(sleep - 7.0) < 1e-6

@pytest.mark.asyncio
async def test_handle_queue_and_owner_sets_owner(setup_manager):
    manager, spotify, queue, feedback, currency = setup_manager
    queue.peek_first.return_value = {"track_id": "abc", "owner": "client1"}
    queue.remove_first.return_value = {"track_id": "abc", "owner": "client1"}
    broadcast = AsyncMock()

    await manager._handle_queue_and_owner("abc", broadcast)
    assert manager.current_owner == "client1"
    broadcast.assert_awaited_once()

@pytest.mark.asyncio
async def test_handle_queue_and_owner_force_resets_owner(setup_manager):
    manager, *_ = setup_manager
    manager.current_owner = "clientX"
    broadcast = AsyncMock()
    await manager._handle_queue_and_owner("zzz", broadcast, force=True)
    assert manager.current_owner is None

@pytest.mark.asyncio
async def test_poll_currently_playing_new_track(setup_manager):
    manager, spotify, queue, feedback, currency = setup_manager
    spotify.get_currently_playing.return_value = {
        "is_playing": True,
        "item": {"id": "track123", "duration_ms": 10000},
        "progress_ms": 1000,
    }
    queue.peek_first.return_value = None
    feedback.set_current_track = MagicMock()
    broadcast = AsyncMock()

    sleep_time = await manager.poll_currently_playing(broadcast)
    feedback.set_current_track.assert_called_once_with("track123")
    assert manager.last_track_id == "track123"
    assert sleep_time > 0

@pytest.mark.asyncio
async def test_handle_feedback_like_reward(setup_manager):
    manager, spotify, queue, feedback, currency = setup_manager
    manager.current_owner = "client1"
    feedback.likes = 7
    feedback.dislikes = 0
    currency.get_balance.return_value = 20

    result = await manager.handle_feedback("like_track", total_clients=10, broadcast_queue_length=AsyncMock())
    assert result["event"] == "reward"
    assert result["owner"] == "client1"
    assert result["tokens"] == 20
    currency.add_tokens.assert_called_once()

@pytest.mark.asyncio
async def test_handle_feedback_dislike_skips(setup_manager):
    manager, spotify, queue, feedback, currency = setup_manager
    feedback.dislikes = 7
    feedback.likes = 0
    spotify.get_currently_playing.return_value = {
        "is_playing": True,
        "item": {
            "id": "trackX",
            "name": "Song",
            "artists": [{"name": "Artist"}],
            "album": {"name": "Album", "images": [{"url": "img"}]},
            "duration_ms": 1000,
            "uri": "uriX",
        },
        "progress_ms": 100,
    }

    result = await manager.handle_feedback("dislike_track", total_clients=10, broadcast_queue_length=AsyncMock())
    assert result["event"] == "track_skipped"
    assert "currently_playing" in result
    spotify.skip_track.assert_called_once()

@pytest.mark.asyncio
async def test_handle_feedback_no_majority_returns_none(setup_manager):
    manager, spotify, queue, feedback, currency = setup_manager
    feedback.likes = 1
    feedback.dislikes = 1
    result = await manager.handle_feedback("like_track", total_clients=10, broadcast_queue_length=AsyncMock())
    assert result is None