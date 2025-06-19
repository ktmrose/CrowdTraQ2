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