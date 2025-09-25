import uuid
import json

class IdentityManager:
    def __init__(self):
        # Map session_id -> websocket
        self._clients: dict[str, object] = {}

    def create_session_id(self) -> str:
        """Always generate a new unique session ID."""
        return str(uuid.uuid4())

    def register(self, websocket, session_id: str | None = None) -> str:
        """
        Register a websocket under a session_id.
        If no session_id provided, generate one.
        Returns the session_id used.
        """
        sid = session_id or self.create_session_id()
        self._clients[sid] = websocket
        return sid

    def unregister(self, session_id: str):
        """Remove a client by session_id."""
        self._clients.pop(session_id, None)

    def get_websocket(self, session_id: str):
        """Return the websocket for a given session_id, or None."""
        return self._clients.get(session_id)

    def all_websockets(self):
        """Return all connected websockets."""
        return list(self._clients.values())

    def all_session_ids(self):
        return list(self._clients.keys())

    async def send_to(self, session_id: str, payload: dict):
        """Send a JSON payload to a specific client if connected."""
        ws = self.get_websocket(session_id)
        if ws:
            await ws.send(json.dumps(payload))

    async def broadcast(self, payload: dict):
        """Broadcast a JSON payload to all connected clients."""
        data = json.dumps(payload)
        for ws in self.all_websockets():
            try:
                await ws.send(data)
            except Exception:
                print(f"Failed to send to a client:", ws)                
                pass