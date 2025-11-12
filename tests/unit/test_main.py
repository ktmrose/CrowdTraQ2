import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app import main

@pytest.mark.asyncio
async def test_safe_send_calls_ws_send():
    ws = AsyncMock()
    payload = '{"msg": "hi"}'
    await main.safe_send(ws, payload)
    ws.send.assert_awaited_once_with(payload)

def test_broadcast_queue_length_sends_and_prunes(monkeypatch):
    # Fake client_handler with sync get_queue_length
    fake_handler = MagicMock()
    fake_handler.get_queue_length.return_value = 2
    monkeypatch.setattr(main, "client_handler", fake_handler)

    # Two websockets, one fails
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    ws1.send.side_effect = Exception("fail")
    main.connected_clients.clear()
    main.connected_clients["c1"] = ws1
    main.connected_clients["c2"] = ws2

    # Run broadcast
    asyncio.run(main.broadcast_queue_length())

    # ws2 should have been sent
    ws2.send.assert_awaited_once()
    # ws1 should be pruned
    assert "c1" not in main.connected_clients
    assert "c2" in main.connected_clients

def test_handle_exit_sets_shutdown_event():
    main.shutdown_event.clear()
    main.handle_exit(None, None)
    assert main.shutdown_event.is_set()