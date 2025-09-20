api = {
    "token": "https://accounts.spotify.com/api/token",
    "authorize": "https://accounts.spotify.com/authorize",
    "currently_playing": "https://api.spotify.com/v1/me/player/currently-playing",
    "track_search": "https://api.spotify.com/v1/search",
    "track_lookup": "https://api.spotify.com/v1/tracks/",
    "add_to_queue": "https://api.spotify.com/v1/me/player/queue",
}

request_info = {
    "content_type": "application/x-www-form-urlencoded",
}

ports = {
    "WEBSOCKET_SERVER_PORT": 7890,
    "SPOTIFY_CLIENT_PORT": 8081
}

STARTING_TOKENS = 5
COST_MODIFIER = 2
POPULAR_TRACK_REWARD = 2