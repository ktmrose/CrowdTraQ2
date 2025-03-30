from websockets.asyncio.server import serve
import asyncio
from init import generate_room_code, start_spotify_client, establish_spotify_connection
import json
from config import ports
# from routes import app


room_code = generate_room_code(4)

async def echo(websocket):
    print("A client connected")
    await websocket.send(json.dumps({"room_code" : room_code}))
    async for message in websocket:
        print("Received message from client "  + message)
        # make a message handler here
        await websocket.send("Pong: " + message)

async def start_websocket_server():
    async with serve(echo, "localhost", ports["WEBSOCKET_SERVER_PORT"]) as server:
        print("Session started on port " + str(ports["WEBSOCKET_SERVER_PORT"]) + ". Room code: " + room_code)
        await server.serve_forever() 

async def main():
    spotify_client_thread = start_spotify_client()
    establish_spotify_connection()
    try:
        asyncio.run(start_websocket_server())
        print("Crowdtraq backend online...")

    except KeyboardInterrupt:
        print("Starting shutdown procedure...")
        spotify_client_thread.shutdown()



if __name__ == "__main__":
    asyncio.run(main())