from string import ascii_uppercase
from random import choice

def generate_room_code(length):
    room_code = ''
    for i in range(length):
        room_code = room_code + choice(ascii_uppercase)
    return room_code

