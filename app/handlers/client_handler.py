from app.services.spotify_manager import SpotifyConnectionManager
from app.services.queue_manager import SongQueue, SongFeedback
from app.config.settings import (
    QUEUE_INSUFFICIENT_TOKENS,
    INVALID_TRACK_ID,
    SPOTIFY_API_ERROR,
    UNKNOWN_ACTION,
    GENERAL_ERROR,
    NO_TRACK_PLAYING,
)
class ClientHandler:

    def __init__(self, currency_manager):
        self._songQueue = SongQueue()
        self.song_feedback = SongFeedback()
        self.currency_manager = currency_manager
        self._spotify_connection = SpotifyConnectionManager.get_instance()

    def get_queue_length(self):
        """
        Returns the current song queue.
        """
        return self._songQueue.length()

    def message_handler(self, message, client_id):
        """
        Handles incoming messages from the client and returns appropriate responses.
        """
        self._spotify_connection = SpotifyConnectionManager.get_instance()

        if not isinstance(message, dict):
            return self._error(code=GENERAL_ERROR, message="Message must be a JSON object.")
        elif "action" not in message:
            return self._error(code=UNKNOWN_ACTION, message="Invalid message format. 'action' key is required.")

        action = message["action"]
        data = message.get("data", {})

        match action:
            case "refresh":
                return self.clean_currently_playing()

            case "add_track":
                track_id = data.get("track_id")
                if not track_id:
                    return self._error(code=INVALID_TRACK_ID, message="Missing 'track_id' in request.")

                success, new_balance = self.currency_manager.try_spend(client_id, self._songQueue.length())

                print(f"Client {client_id} attempting to add track {track_id}. Success: {success}, New Balance: {new_balance}")
                if not success:
                    return self._error(
                        code=QUEUE_INSUFFICIENT_TOKENS,
                        message="You don\'t have enough tokens to add this song.",
                        details={"requiredTokens": self.currency_manager.calculate_cost(self._songQueue.length()), "availableTokens": new_balance}
                    )

                response = self._spotify_connection.add_track_by_id(track_id)
                if hasattr(response, "status_code") and response.status_code == 200:
                    self._songQueue.add(track_id, client_id)
                    return {"success": True, "tokens": new_balance}
                else:
                    return self._error(
                        code=SPOTIFY_API_ERROR,
                        message="Failed to add track to Spotify queue.",
                        details={"tokens": new_balance}
                    )

            case "like_track":
                self.song_feedback.like(client_id)
                return self.check_currently_playing()
                

            case "dislike_track":
                self.song_feedback.dislike(client_id)
                return self.check_currently_playing()

            case "search":
                query = data.get("query", "")
                return self.search_song(query)
            case _:
                return self._error(code=UNKNOWN_ACTION, message=f"Unknown action: {action}")

    def check_currently_playing(self):
        current = self._currently_playing or self._spotify_connection.get_currently_playing()
        if not current or not current.get("item"):
            return self._error(code=NO_TRACK_PLAYING, message="No track is currently playing.")

        track_id = current["item"].get("id")
        if not track_id:
            return self._error(code=INVALID_TRACK_ID, message="Unable to determine track ID.")
        return {"success": True}

    def _error(self, code: str, message: str, details: dict | None = None):
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            }
        }

    def clean_currently_playing(self):
        """
        Extracts and formats relevant info from Spotify's currently playing API response.
        """
        if self._spotify_connection is None:
            raise Exception("Spotify connection is not established. Please ensure SpotifyConnection instance runs as expected.")

        self._currently_playing = self._spotify_connection.get_currently_playing()
        if self._currently_playing is None:
            return self._error(code=NO_TRACK_PLAYING, message="No track is currently playing.")
        
        item = self._currently_playing.get("item", {})

        return { "currently_playing":{
            "track_name": item.get("name"),
            "artists": [artist.get("name") for artist in item.get("artists", [])],
            "album": item.get("album", {}).get("name"),
            "album_art": item.get("album", {}).get("images", [{}])[0].get("url"),
            "duration_ms": item.get("duration_ms"),
            "progress_ms": self._currently_playing.get("progress_ms"),
            "is_playing": self._currently_playing.get("is_playing"),
            "track_id": item.get("id"),
            "uri": item.get("uri"),
        }}

    def search_song(self, input):
        """
        Looks up a track by its ID and returns its details.
        """
        track_info = self._spotify_connection.search_songs(input)

        if not track_info:
            return None

        items = track_info["tracks"].get("items", [])
        data = [
            {
                "track_name": item.get("name"),
                "artists": [artist.get("name") for artist in item.get("artists", [])],
                "track_id": item.get("id"),
                "album_art": item.get("album", {}).get("images", [{}])[0].get("url"),
            }
            for item in items
        ]

        return {"search_data": data}