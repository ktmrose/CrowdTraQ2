from websockets.asyncio.server import serve
import asyncio
from init import generate_room_code, establish_spotify_connection
import json
from config import ports
from routes import app
from threading import Thread


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

async def start_spotify_client():
    print("Starting Spotify client on port " + str(ports["SPOTIFY_CLIENT_PORT"]))
    app.run(port=ports["SPOTIFY_CLIENT_PORT"])

async def main():
    # establish_spotify_connection()
    spotify_client_thread = Thread(target=start_spotify_client)
    spotify_client_thread.start()

    await start_websocket_server()


if __name__ == "__main__":
    asyncio.run(main())