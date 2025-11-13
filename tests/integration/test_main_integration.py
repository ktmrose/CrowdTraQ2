import pytest
import asyncio
import json
import websockets
from unittest.mock import MagicMock

@pytest.fixture
def fake_spotify(monkeypatch):
    class FakeResponse:
        def __init__(self, status_code=200):
            self.status_code = status_code

    fake_conn = MagicMock()
    fake_conn.token_info = {"access_token": "fake-token"}
    fake_conn.credentials = {"access_token": "fake-token"}
    fake_conn._spotify_user_token = "fake-token"
    fake_conn._token_expiration = 9999999999  # far future

    fake_conn.get_currently_playing.return_value = {
        "item": {
            "id": "t123",
            "name": "Fake Track",
            "artists": [{"name": "Fake Artist"}],
            "album": {"name": "Fake Album", "images": [{"url": "http://fake"}]},
            "duration_ms": 180000,
            "uri": "spotify:track:t123"
        },
        "progress_ms": 1000,
        "is_playing": True
    }

    fake_conn.add_track_by_id.return_value = FakeResponse(200)
    fake_conn.search_songs.return_value = {
        "tracks": {
            "items": [{
                "id": "t123",
                "name": "Fake Track",
                "artists": [{"name": "Fake Artist"}],
                "album": {"images": [{"url": "http://fake"}]}
            }]
        }
    }

    monkeypatch.setattr("app.handlers.client_handler.SpotifyConnectionManager.get_instance", lambda: fake_conn)
    return fake_conn

@pytest.mark.asyncio
async def test_client_connector_add_track_flow(fake_spotify):
    from app import main
    server = await websockets.serve(main.client_connector, "localhost", 8765)

    async with websockets.connect("ws://localhost:8765") as ws:
        # Send hello payload
        await ws.send(json.dumps({"sessionId": "abc"}))
        init_payload = json.loads(await ws.recv())
        assert init_payload["sessionId"] == "abc"
        assert "tokens" in init_payload

        # Send add_track
        await ws.send(json.dumps({"action": "add_track", "data": {"track_id": "t123"}}))
        response = json.loads(await ws.recv())
        assert response["success"] is True
        assert "tokens" in response

        # Send like_track
        await ws.send(json.dumps({"action": "like_track"}))
        response = json.loads(await ws.recv())
        assert response["success"] is True

        # Send refresh
        await ws.send(json.dumps({"action": "refresh"}))
        response = json.loads(await ws.recv())
        assert "currently_playing" in response
        assert response["currently_playing"]["track_id"] == "t123"

    server.close()
    await server.wait_closed()