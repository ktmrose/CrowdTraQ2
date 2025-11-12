import pytest
from app.services.queue_manager import SongQueue, SongFeedback

# -------------------------
# SongQueue tests
# -------------------------

def test_add_and_length():
    q = SongQueue()
    q.add("track1", "clientA")
    q.add("track2", "clientB")
    assert q.length() == 2
    assert q.as_list() == [
        {"track_id": "track1", "owner": "clientA"},
        {"track_id": "track2", "owner": "clientB"},
    ]

def test_peek_first_and_remove_first_success():
    q = SongQueue()
    q.add("track1", "clientA")
    q.add("track2", "clientB")

    first = q.peek_first()
    assert first["track_id"] == "track1"

    removed = q.remove_first("track1")
    assert removed == {"track_id": "track1", "owner": "clientA"}
    assert q.length() == 1
    assert q.peek_first()["track_id"] == "track2"

def test_remove_first_wrong_id_returns_none():
    q = SongQueue()
    q.add("track1", "clientA")
    result = q.remove_first("trackX")
    assert result is None
    assert q.length() == 1

def test_peek_first_empty_returns_none():
    q = SongQueue()
    assert q.peek_first() is None

# -------------------------
# SongFeedback tests
# -------------------------

def test_set_current_track_resets_votes():
    fb = SongFeedback()
    fb.like("user1")
    fb.dislike("user2")
    assert fb.likes == 1
    assert fb.dislikes == 1

    fb.set_current_track("track1")
    assert fb.current_track_id == "track1"
    assert fb.votes == {}

def test_like_and_dislike_and_get_vote():
    fb = SongFeedback()
    fb.set_current_track("track1")
    fb.like("user1")
    fb.dislike("user2")

    assert fb.get_vote("user1") == "like"
    assert fb.get_vote("user2") == "dislike"
    assert fb.get_vote("ghost") is None

def test_likes_and_dislikes_properties():
    fb = SongFeedback()
    fb.set_current_track("track1")
    fb.like("u1")
    fb.like("u2")
    fb.dislike("u3")

    assert fb.likes == 2
    assert fb.dislikes == 1