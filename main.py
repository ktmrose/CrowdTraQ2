from websockets.asyncio.server import serve
import asyncio
from init import generate_room_code, start_spotify_client, establish_spotify_connection
import json
from config import ports
import signal

room_code = generate_room_code(4)
shutdown_event = asyncio.Event()

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
        await shutdown_event.wait()

async def main():
    spotify_client_thread = start_spotify_client()
    establish_spotify_connection()
    try:
        await start_websocket_server()
        print("Crowdtraq backend online...")

    except KeyboardInterrupt:
        pass
    finally:
        print("Starting shutdown procedure...")
        spotify_client_thread.shutdown()
        shutdown_event.set()

def handle_exit(signum, frame):
    print("Caught termination signal. Shutting down...")
    shutdown_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    asyncio.run(main())