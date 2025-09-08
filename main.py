from websockets.asyncio.server import serve
import asyncio
from init import generate_room_code, start_spotify_client, establish_spotify_connection
import json
from config import ports
import signal
from handlers import ClientHandler 
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
                duration = info["item"]["duration_ms"]
                progress = info.get("progress_ms", 0)
                # Calculate time left, poll 2 seconds before the song ends, but not less than 1 second
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
    message = json.dumps({"queue_length": queue_length})
    print(f"Broadcasting queue length {queue_length} to {len(connected_clients)} clients")
    await asyncio.gather(*(client.send(message) for client in connected_clients if not client.close))

async def client_connector(websocket):
    print("Clients connected:", len(connected_clients) + 1)
    connected_clients.add(websocket)
    try:
        currently_playing = client_handler.clean_currently_playing()
    except Exception as e:
        print("Error getting currently playing track:", e)
    
    print("Currently playing track:", currently_playing)
    await websocket.send(json.dumps({"room_code" : room_code, "currently_playing": currently_playing}))
    
    async for message in websocket:
        response = client_handler.message_handler(json.loads(message))
        print("Received message:", response)
        if response.get("status"):
            await broadcast_queue_length()
        await websocket.send(json.dumps(response))
    
    connected_clients.remove(websocket)

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