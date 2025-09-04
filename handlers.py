from spotify_manager import SpotifyConnectionManager
class ClientHandler:

    def __init__(self):
        self._songQueue = []
        self._currently_playing = None
        self._spotify_connection = SpotifyConnectionManager.get_instance()

    def get_queue_length(self):
        """
        Returns the current song queue.
        """
        return len(self._songQueue)

    def message_handler(self, message):
        """
        Handles incoming messages from the client and returns appropriate responses.
        """
        self._spotify_connection = SpotifyConnectionManager.get_instance()

        if not isinstance(message, dict):
            return {"error": "Message must be a JSON object."}
        elif "action" not in message:
            return {"error": "Invalid message format. 'action' key is required."}

        action = message["action"]
        data = message.get("data", {})

        match action:
            case "refresh":
                currently_playing = self._spotify_connection.get_currently_playing()
                return self.clean_currently_playing(currently_playing)

            case "add_track":
                track_id = data.get("track_id")
                if not track_id:
                    return {"status": False, "error": "Missing 'track_id' in message."}
                response = self._spotify_connection.add_track_by_id(track_id)
                if hasattr(response, "status_code") and response.status_code == 200:
                    self._songQueue.append(track_id)
                    return {"status": True}
                else:
                    return {"status": False, "error": "Failed to add track to Spotify queue."}

            case "like_track":
                # Like currently playing track
                print("Someone likes this track")
                return None  # Placeholder for liking functionality

            case "dislike_track":
                # Dislike currently playing track
                print("Someone dislikes this track")
                return None  # Placeholder for disliking functionality

            case "search":
                query = data.get("query", "")
                return self.search_song(query)
            case _:
                return {"status": False, "error": f"Unknown action: {action}"}

    def clean_currently_playing(self):
        """
        Extracts and formats relevant info from Spotify's currently playing API response.
        """
        if self._spotify_connection is None:
            raise Exception("Spotify connection is not established. Please ensure SpotifyConnection instance runs as expected.")

        self._currently_playing = self._spotify_connection.get_currently_playing()
        if self._currently_playing is None:
            return None
        
        item = self._currently_playing.get("item", {})

        return {
            "track_name": item.get("name"),
            "artists": [artist.get("name") for artist in item.get("artists", [])],
            "album": item.get("album", {}).get("name"),
            "album_art": item.get("album", {}).get("images", [{}])[0].get("url"),
            "duration_ms": item.get("duration_ms"),
            "progress_ms": self._currently_playing.get("progress_ms"),
            "is_playing": self._currently_playing.get("is_playing"),
            "track_id": item.get("id"),
            "uri": item.get("uri"),
        }

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