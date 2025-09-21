# app/services/playback_manager.py

from app.config import settings

class PlaybackManager:
    def __init__(self, spotify_connection, song_queue, song_feedback, currency_manager):
        self.spotify = spotify_connection
        self.queue = song_queue
        self.feedback = song_feedback
        self.currency = currency_manager
        self.current_owner = None
        self.last_track_id = None

    async def poll_currently_playing(self, broadcast_queue_length):
        info = self.spotify.get_currently_playing()
        if info and info.get("is_playing"):
            track_id = info["item"]["id"]
            # Check if the first item in our queue matches the current track
            first_in_queue = self.queue.peek_first()
            if first_in_queue and first_in_queue["track_id"] == track_id:
                print(f"Current track {track_id} matches queue front. Removing from queue.")
                removed = self.queue.remove_first(track_id)
                if removed:
                    print(f"Removed {track_id} from queue")
                    await broadcast_queue_length()

            # Always reset feedback when track changes OR when queue advances
            self.feedback.set_current_track(track_id)

            # Calculate sleep time until near end of track
            duration = info["item"]["duration_ms"]
            progress = info.get("progress_ms", 0)
            time_left = max((duration - progress) / 1000.0 - 1, .5)
            return time_left

        print("Nothing playing, polling again in 5 seconds")
        return 5  # nothing playing, poll again in 5s

    def request_reward(self, total_clients: int):
        if total_clients > 0 and self.feedback.likes > total_clients * 0.66:
            self.currency.add_tokens(self.current_owner, settings.POPULAR_TRACK_REWARD)
            print(f"Rewarded {self.current_owner} with {settings.POPULAR_TRACK_REWARD} tokens for popular track")
        return None