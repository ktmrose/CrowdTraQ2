from websockets.asyncio.server import serve
import asyncio
from string import ascii_uppercase
from random import choice

PORT = 7890

def generate_room_code(length):
    room_code = ''
    for i in range(length):
        room_code = room_code + choice(ascii_uppercase)
    return room_code
    

async def echo(websocket):
    print("A client connected")
    async for message in websocket:
        print("Received message from client "  + message)
        await websocket.send("Pong: " + message)

async def main():
    async with serve(echo, "localhost", PORT) as server:
        print("Session started. Room code: " + generate_room_code(4))
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())