api = {
    "token": "https://accounts.spotify.com/api/token",
    "authorize": "https://accounts.spotify.com/authorize",
    "currently_playing": "https://api.spotify.com/v1/me/player/currently-playing",
    "track_search": "https://api.spotify.com/v1/search",
    "track_lookup": "https://api.spotify.com/v1/tracks/",
    "add_to_queue": "https://api.spotify.com/v1/me/player/queue",
    "next_song": "https://api.spotify.com/v1/me/player/next",
}

request_info = {
    "content_type": "application/x-www-form-urlencoded",
}

ports = {
    "WEBSOCKET_SERVER_PORT": 7890,
    "SPOTIFY_CLIENT_PORT": 8081
}

STARTING_TOKENS = 1 # change to 5 for beta test
COST_MODIFIER = 2
POPULAR_TRACK_REWARD = 2

QUEUE_INSUFFICIENT_TOKENS = "QUEUE_INSUFFICIENT_TOKENS"
INVALID_TRACK_ID = "INVALID_TRACK_ID"
SPOTIFY_API_ERROR = "SPOTIFY_API_ERROR"
UNKNOWN_ACTION = "UNKNOWN_ACTION"
UNKNOWN_USER = "UNKNOWN_USER"
GENERAL_ERROR = "GENERAL_ERROR"
NO_TRACK_PLAYING = "NO_TRACK_PLAYING"
