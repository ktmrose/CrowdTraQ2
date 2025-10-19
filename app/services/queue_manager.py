class SongQueue:
    def __init__(self):
        self._queue = []

    def add(self, track_id, client_id):
        self._queue.append({"track_id": track_id, "owner": client_id})

    def remove_first(self, track_id):
        if self._queue and self._queue[0]["track_id"] == track_id:
            return self._queue.pop(0)
        return None

    def peek_first(self):
        return self._queue[0] if self._queue else None

    def length(self):
        return len(self._queue)

    def as_list(self):
        return list(self._queue)
    
class SongFeedback:
    def __init__(self):
        self.current_track_id = None
        self.votes = {}  # { session_id: "like" | "dislike" }

    def set_current_track(self, track_id: str):
        if track_id != self.current_track_id:
            # reset votes when track changes
            self.current_track_id = track_id
            self.votes.clear()

    def like(self, session_id: str):
        self.votes[session_id] = "like"

    def dislike(self, session_id: str):
        self.votes[session_id] = "dislike"

    def get_vote(self, session_id: str) -> str | None:
        """Return 'like', 'dislike', or None if this client hasn't voted."""
        return self.votes.get(session_id)

    @property
    def likes(self) -> int:
        return sum(1 for v in self.votes.values() if v == "like")

    @property
    def dislikes(self) -> int:
        return sum(1 for v in self.votes.values() if v == "dislike")