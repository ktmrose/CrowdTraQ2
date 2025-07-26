def message_handler(message):
    """
    Handles incoming messages from the client and returns appropriate responses.
    """
    from spotify_manager import SpotifyConnectionManager
    spotify_connection = SpotifyConnectionManager.get_instance()

    if "action" not in message:
        return {"error": "Invalid message format. 'action' key is required."}

    action = message["action"]

    match action:
        case "refresh":
            currently_playing = spotify_connection.get_currently_playing()
            return clean_currently_playing(currently_playing)

        case "add_track":
            track_id = message.get("track_id")
            if not track_id:
                return {"error": "Missing 'track_id' in message."}
            spotify_connection.add_track_by_id(track_id)
            return {"status": "Track added to queue."}

        case "like_track":
            # Like currently playing track
            return None  # Placeholder for liking functionality

        case "dislike_track":
            # Dislike currently playing track
            return None  # Placeholder for disliking functionality

        case _:
            return {"error": f"Unknown action: {action}"}

def clean_currently_playing(spotify_response):
    """
    Extracts and formats relevant info from Spotify's currently playing API response.
    """
    if not spotify_response:
        return None

    item = spotify_response.get("item")
    if not item:
        return None

    return {
        "track_name": item.get("name"),
        "artists": [artist.get("name") for artist in item.get("artists", [])],
        "album": item.get("album", {}).get("name"),
        "album_art": item.get("album", {}).get("images", [{}])[0].get("url"),
        "duration_ms": item.get("duration_ms"),
        "progress_ms": spotify_response.get("progress_ms"),
        "is_playing": spotify_response.get("is_playing"),
        "track_id": item.get("id"),
        "uri": item.get("uri"),
    }

def search_song(input):
    """
    Looks up a track by its ID and returns its details.
    """
    from spotify_manager import SpotifyConnectionManager
    spotify_connection = SpotifyConnectionManager.get_instance()
    track_info = spotify_connection.search_track(input)

    if not track_info:
        return None

    return {
        "track_name": track_info.get("name"),
        "artists": [artist.get("name") for artist in track_info.get("artists", [])],
        "album": track_info.get("album", {}).get("name"),
        "album_art": track_info.get("album", {}).get("images", [{}])[0].get("url"),
        "duration_ms": track_info.get("duration_ms"),
        "track_id": track_info.get("id"),
        "uri": track_info.get("uri"),
    }