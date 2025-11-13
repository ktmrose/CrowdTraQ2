import pytest
from app.handlers.client_handler import ClientHandler

@pytest.mark.asyncio
async def test_message_handler_add_track(currency_manager, song_queue, song_feedback):
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
async def test_message_handler_vote_track(currency_manager, song_queue, song_feedback):
    handler = ClientHandler(currency_manager)
    handler._songQueue = song_queue
    handler.song_feedback = song_feedback

    client_id = "client2"
    currency_manager.register_client(client_id)

    song_feedback.set_current_track("t999")

    message = {"action": "like_track"}
    response = handler.message_handler(message, client_id)

    assert response["success"] is True
    assert song_feedback.get_vote(client_id) == "like"

    message = {"action": "dislike_track"}
    response = handler.message_handler(message, client_id)

    assert response["success"] is True
    assert song_feedback.get_vote(client_id) == "dislike"

@pytest.mark.asyncio
async def test_add_track_missing_id(currency_manager):
    handler = ClientHandler(currency_manager)
    client_id = "client3"
    currency_manager.register_client(client_id)
    currency_manager.add_tokens(client_id, 10)

    message = {"action": "add_track", "data": {}}
    response = handler.message_handler(message, client_id)

    assert response["success"] is False
    assert response["error"]["code"] == "INVALID_TRACK_ID"