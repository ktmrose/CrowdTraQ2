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

def user_search_songs(spotify_connection, query):
    """
    Searches for songs using the Spotify API.
    """
    if not spotify_connection:
        raise Exception("Spotify connection is not established. Please ensure SpotifyConnection instance runs as expected.")
    
    try:
        results = spotify_connection.search_songs(query, limit=10)
        return results.get('tracks', {}).get('items', [])
    except Exception as e:
        print("Error searching for songs:", e)
        return []
    
def handle_user_message(message, spotify_connection):
    """
    Handles user messages received from the WebSocket.
    """
    if not spotify_connection:
        raise Exception("Spotify connection is not established. Please ensure SpotifyConnection instance runs as expected.")
    
    if message.startswith("search:"):
        query = message[len("search:"):].strip()
        search_results = user_search_songs(spotify_connection, query)
        response = {
            "type": "search_results",
            "results": search_results
        }
        return response
    else:
        # Handle other message types here
        pass