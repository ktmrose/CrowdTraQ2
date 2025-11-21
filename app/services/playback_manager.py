from app.config import settings
import logging

logger = logging.getLogger("app.core.playback_manager")

class PlaybackManager:
    def __init__(self, spotify_connection, song_queue, song_feedback, currency_manager):
        self.spotify = spotify_connection
        self.queue = song_queue
        self.feedback = song_feedback
        self.currency = currency_manager
        self.current_owner = None
        self.last_track_id = None

    def _get_current_track_id(self, info: dict) -> str | None:
        if not info or not info.get("is_playing"):
            return None
        return info["item"]["id"]

    async def _handle_queue_and_owner(self, track_id: str, broadcast_queue_length, force=False):
        """
        Update current_owner based on the queue.
        - If the first item matches the current track, pop it and set owner.
        - If force=True, treat it as a new play even if track_id == last_track_id
        (used for duplicate songs queued back-to-back).
        """
        first_in_queue = self.queue.peek_first()
        if first_in_queue and first_in_queue["track_id"] == track_id:
            removed = self.queue.remove_first(track_id)
            if removed:
                self.current_owner = removed["owner"]
                await broadcast_queue_length()
        elif force:
            # Explicit reset even if not in queue
            self.current_owner = None
        # else: leave current_owner unchanged


    def _calculate_sleep_time(self, info: dict) -> float:
        duration = info["item"]["duration_ms"]
        progress = info.get("progress_ms", 0)
        return max((duration - progress) / 1000.0 - 1, 0.5)


    async def poll_currently_playing(self, broadcast_queue_length):
        info = self.spotify.get_currently_playing()
        track_id = self._get_current_track_id(info)

        if not track_id:
            logger.debug("Nothing playing, polling again in 5 seconds")
            return 5

        # Case 1: brand new track ID
        if track_id != self.last_track_id:
            logger.info(f"New track detected: {track_id}, updating queue and owner")
            await self._handle_queue_and_owner(track_id, broadcast_queue_length)
            self.feedback.set_current_track(track_id)
            self.last_track_id = track_id

        # Case 2: same track ID, but another queued entry exists
        elif self.queue.peek_first() and self.queue.peek_first()["track_id"] == track_id:
            logger.info(f"Track {track_id} replayed from queue, updating owner")
            await self._handle_queue_and_owner(track_id, broadcast_queue_length)
            self.feedback.set_current_track(track_id)  # reset feedback for new play

        # Case 3: same track still playing, no queue entry → do nothing

        return self._calculate_sleep_time(info)

    async def handle_feedback(self, action: str, total_clients: int, broadcast_queue_length):
        if action == "like_track" and total_clients > 0 and self.feedback.likes > total_clients * 0.66:
            logger.info("Track liked by supermajority, rewarding owner...")
            self.currency.add_tokens(self.current_owner, settings.POPULAR_TRACK_REWARD)
            return {
                "event": "reward",
                "owner": self.current_owner,
                "tokens": self.currency.get_balance(self.current_owner)
            }

        if action == "dislike_track" and total_clients > 0 and self.feedback.dislikes > total_clients * 0.66:
            logger.info("Track disliked by supermajority, skipping...")
            self.spotify.skip_track()
            # immediately re‑poll to update state and broadcast new track
            await self.poll_currently_playing(broadcast_queue_length)
            info = self.spotify.get_currently_playing()
            return {
                "event": "track_skipped",
                "currently_playing": {
                    "track_name": info["item"]["name"],
                    "artists": [a["name"] for a in info["item"]["artists"]],
                    "album": info["item"]["album"]["name"],
                    "album_art": info["item"]["album"]["images"][0]["url"],
                    "duration_ms": info["item"]["duration_ms"],
                    "progress_ms": info.get("progress_ms"),
                    "is_playing": info.get("is_playing"),
                    "track_id": info["item"]["id"],
                    "uri": info["item"]["uri"],
                }
            }

        return None