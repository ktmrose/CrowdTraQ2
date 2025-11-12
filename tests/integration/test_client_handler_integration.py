import pytest
import json
from unittest.mock import MagicMock
from app.handlers.client_handler import ClientHandler

@pytest.mark.asyncio
async def test_message_handler_add_track(currency_manager, song_queue, song_feedback, fake_spotify):
    handler = ClientHandler(currency_manager)
    handler._songQueue = song_queue
    handler.song_feedback = song_feedback

    client_id = "client1"
    currency_manager.register_client(client_id)
    currency_manager.add_tokens(client_id, 10)

    message = {"action": "add_track", "data": {"track_id": "t123"}}
    response = handler.message_handler(message, client_id)

    assert response["success"] is True
    assert song_queue.peek_first()["track_id"] == "t123"

@pytest.mark.asyncio
async def test_message_handler_vote_track(currency_manager, song_queue, song_feedback, fake_spotify):
    """
    Integration test: simulate a client voting on a track.
    """
    handler = ClientHandler(currency_manager)
    handler._spotify_connection = fake_spotify
    handler._songQueue = song_queue
    handler.song_feedback = song_feedback

    client_id = "client2"
    currency_manager.register_client(client_id)

    # Set current track in feedback
    song_feedback.set_current_track("t999")

    # Simulate a like vote
    message = {"action": "like_track"}
    response = handler.message_handler(message, client_id)

    assert response["success"] is True
    assert song_feedback.get_vote(client_id) == "like"

    # Simulate a dislike vote
    message = {"action": "dislike_track"}
    response = handler.message_handler(message, client_id)

    assert response["success"] is True
    assert song_feedback.get_vote(client_id) == "dislike"