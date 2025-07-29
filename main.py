from websockets.asyncio.server import serve
import asyncio
from init import generate_room_code, start_spotify_client, establish_spotify_connection
import json
from config import ports
import signal
from spotify_manager import SpotifyConnectionManager
from handlers import clean_currently_playing, message_handler
import time

room_code = generate_room_code(4)
shutdown_event = asyncio.Event()
spotify_connection = SpotifyConnectionManager.get_instance()

async def client_connector(websocket):
    print("A client connected")

    currently_playing = None
    if spotify_connection is None:
        raise Exception("Spotify connection is not established. PLease ensure SpotifyConnection instance runs as expected.")
    try:
        currently_playing = spotify_connection.get_currently_playing()
        cleaned_currently_playing = clean_currently_playing(currently_playing)
    except Exception as e:
        print("Error getting currently playing track:", e)
    
    print("Currently playing track:", cleaned_currently_playing)
    await websocket.send(json.dumps({"room_code" : room_code, "currently_playing": cleaned_currently_playing}))
    
    async for message in websocket:
        response = message_handler(json.loads(message))
        await websocket.send(json.dumps(response))

async def start_websocket_server():
    async with serve(client_connector, "localhost", ports["WEBSOCKET_SERVER_PORT"]) as server:
        print("Session started on port " + str(ports["WEBSOCKET_SERVER_PORT"]) + ". Room code: " + room_code)
        await shutdown_event.wait()

async def main():
    spotify_client_thread = start_spotify_client()
    establish_spotify_connection()
    try:
        await start_websocket_server()
        print("Crowdtraq websocket thread shutdown...")

    except KeyboardInterrupt:
        pass
    
    finally:
        shutdown_start = time.time()
        print("Starting shutdown procedure. This may take up to 15 minutes until I get around to fixing this")
        spotify_client_thread.shutdown()
        spotify_client_thread.join(timeout=5)
        print("Spotify client thread has been shut down.")
        shutdown_event.set()
        shutdown_end = time.time()
        print(f"Shutdown took {shutdown_end - shutdown_start:.2f} seconds.")

def handle_exit(signum, frame):
    print("Caught termination signal. Shutting down...")
    shutdown_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    asyncio.run(main())