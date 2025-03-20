from string import ascii_uppercase
from random import choice
from spotify import SpotifyConnection

def generate_room_code(length):
    room_code = ''
    for i in range(length):
        room_code = room_code + choice(ascii_uppercase)
    return room_code

def establish_spotify_connection():
    spotify_connection = SpotifyConnection()
    spotify_connection.initialize_access_token()
    print(spotify_connection.get_access_token())