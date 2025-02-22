from websockets.asyncio.server import serve
import asyncio
from init import generate_room_code
import json

PORT = 7890
room_code = generate_room_code(4)

async def echo(websocket):
    print("A client connected")
    await websocket.send(json.dumps({"room_code" : room_code}))
    async for message in websocket:
        print("Received message from client "  + message)
        # make a message handler here
        await websocket.send("Pong: " + message)

async def main():
    
    async with serve(echo, "localhost", PORT) as server:
        print("Session started on port " + str(PORT) + ". Room code: " + room_code)
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())