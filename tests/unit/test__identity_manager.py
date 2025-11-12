import pytest
import asyncio
from unittest.mock import AsyncMock
from app.services.identity_manager import IdentityManager

def test_create_session_id_unique():
    im = IdentityManager()
    sid1 = im.create_session_id()
    sid2 = im.create_session_id()
    assert isinstance(sid1, str)
    assert sid1 != sid2  # should be unique

def test_register_and_get_websocket():
    im = IdentityManager()
    fake_ws = object()
    sid = im.register(fake_ws)
    assert im.get_websocket(sid) is fake_ws
    assert sid in im.all_session_ids()
    assert fake_ws in im.all_websockets()

def test_register_with_provided_session_id():
    im = IdentityManager()
    fake_ws = object()
    sid = im.register(fake_ws, session_id="abc123")
    assert sid == "abc123"
    assert im.get_websocket("abc123") is fake_ws

def test_unregister_removes_client():
    im = IdentityManager()
    fake_ws = object()
    sid = im.register(fake_ws)
    im.unregister(sid)
    assert im.get_websocket(sid) is None
    assert sid not in im.all_session_ids()

@pytest.mark.asyncio
async def test_send_to_calls_ws_send():
    im = IdentityManager()
    fake_ws = AsyncMock()
    sid = im.register(fake_ws)
    payload = {"msg": "hello"}

    await im.send_to(sid, payload)

    fake_ws.send.assert_awaited_once_with('{"msg": "hello"}')

@pytest.mark.asyncio
async def test_send_to_no_client_does_nothing():
    im = IdentityManager()
    payload = {"msg": "hello"}
    # no clients registered
    await im.send_to("ghost", payload)  # should not raise

@pytest.mark.asyncio
async def test_broadcast_sends_to_all():
    im = IdentityManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    im.register(ws1, "sid1")
    im.register(ws2, "sid2")

    payload = {"msg": "broadcast"}
    await im.broadcast(payload)

    ws1.send.assert_awaited_once_with('{"msg": "broadcast"}')
    ws2.send.assert_awaited_once_with('{"msg": "broadcast"}')

@pytest.mark.asyncio
async def test_broadcast_handles_exception():
    im = IdentityManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    ws1.send.side_effect = Exception("fail")
    im.register(ws1, "sid1")
    im.register(ws2, "sid2")

    payload = {"msg": "broadcast"}
    # Should not raise even though ws1.send fails
    await im.broadcast(payload)

    ws2.send.assert_awaited_once()