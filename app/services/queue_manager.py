class SongQueue:
    def __init__(self):
        self._queue = []

    def add(self, track_id):
        self._queue.append(track_id)

    def remove_first(self, track_id):
        try:
            self._queue.remove(track_id)  # removes first occurrence only
            return True
        except ValueError:
            return False

    def length(self):
        return len(self._queue)

    def as_list(self):
        return list(self._queue)
    
class SongFeedback:
    def __init__(self):
        self._current_track_id = None
        self.likes = 0
        self.dislikes = 0

    def set_current_track(self, track_id):
        if track_id != self._current_track_id:
            self._current_track_id = track_id
            self.likes = 0
            self.dislikes = 0

    def like(self):
        self.likes += 1

    def dislike(self):
        self.dislikes += 1

    def get_feedback(self):
        return {"likes": self.likes, "dislikes": self.dislikes}