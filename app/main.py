from websockets.asyncio.server import serve
import asyncio
from app.core.init_app import generate_room_code, start_spotify_client, establish_spotify_connection
import json
from app.config.settings import ports
import signal
from app.handlers.client_handler import ClientHandler 
import time

room_code = generate_room_code(4)
shutdown_event = asyncio.Event()
connected_clients = set()

client_handler = ClientHandler()

async def poll_currently_playing():
    while True:
        try:
            info = client_handler._spotify_connection.get_currently_playing()
            if info and info.get("is_playing"):
                track_id = info["item"]["id"]
                
                # Check if the first item in our queue matches the current track
                first_in_queue = client_handler._songQueue.peek_first()
                if first_in_queue == track_id:
                    removed = client_handler._songQueue.remove_first(track_id)
                    if removed:
                        print(f"Removed {track_id} from queue")
                        await broadcast_queue_length()

                # Always reset feedback when track changes OR when queue advances
                client_handler.song_feedback.set_current_track(track_id)

                # Sleep until near the end of the song

                duration = info["item"]["duration_ms"]
                progress = info.get("progress_ms", 0)
                time_left = max((duration - progress) / 1000.0 - 2, 1)
                print(f"Song playing, polling again in {time_left:.1f} seconds")
                await asyncio.sleep(time_left)
            else:
                print("Nothing playing, polling again in 5 seconds")
                await asyncio.sleep(5)
        except Exception as e:
            print("Error polling currently playing:", e)
            await asyncio.sleep(5)

async def broadcast_queue_length():
    queue_length = client_handler.get_queue_length()
    payload = json.dumps({"queue_length": queue_length})
    targets = list(connected_clients)  # snapshot to avoid concurrent modification
    print(f"Broadcasting queue length {queue_length} to {len(targets)} clients")

    results = await asyncio.gather(
        *(safe_send(ws, payload) for ws in targets),
        return_exceptions=True,
    )

    for ws, result in zip(targets, results):
        if isinstance(result, Exception):
            print(f"Pruning client {ws}: {result}")
            connected_clients.discard(ws)

async def safe_send(ws, payload):
    await ws.send(payload)  # exceptions bubble up to broadcast

async def client_connector(websocket):
    connected_clients.add(websocket)
    try:
        try:
            currently_playing = client_handler.clean_currently_playing()
        except Exception as e:
            print("Error getting currently playing track:", e)
            currently_playing = {}

        # Unicast initial state to this client
        await websocket.send(json.dumps(currently_playing))
        await websocket.send(json.dumps({"queue_length": client_handler.get_queue_length()}))

        # Optionally also broadcast so everyone else sees updates triggered by this join
        await broadcast_queue_length()

        async for raw in websocket:
            response = client_handler.message_handler(json.loads(raw))
            if response.get("status"):
                await broadcast_queue_length()
            await websocket.send(json.dumps(response))

    except Exception as e:
        print("Error in client_connector:", e)

    finally:
        connected_clients.discard(websocket)


async def start_websocket_server():
    async with serve(client_connector, "localhost", ports["WEBSOCKET_SERVER_PORT"]) as server:
        print("Session started on port " + str(ports["WEBSOCKET_SERVER_PORT"]) + ". Room code: " + room_code)
        await shutdown_event.wait()

async def main():
    spotify_client_thread = start_spotify_client()
    establish_spotify_connection()
    poll_task = asyncio.create_task(poll_currently_playing())
    try:
        await start_websocket_server()
        print("Crowdtraq websocket thread shutdown...")

    except KeyboardInterrupt:
        pass
    
    finally:
        poll_task.cancel()
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