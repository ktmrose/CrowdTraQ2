from websockets.asyncio.server import serve
import asyncio, json, signal, time

from app.core.init_app import generate_room_code, start_spotify_client, establish_spotify_connection
from app.config.settings import ports
from app.services.currency_manager import CurrencyManager
from app.services.playback_manager import PlaybackManager
from app.handlers.client_handler import ClientHandler

room_code = generate_room_code(4)
shutdown_event = asyncio.Event()
connected_clients = {}

currency_manager = CurrencyManager()
client_handler = ClientHandler(currency_manager)

# Playback manager orchestrates queue + feedback + rewards
playback_manager = PlaybackManager(
    client_handler._spotify_connection,
    client_handler._songQueue,
    client_handler.song_feedback,
    currency_manager
)

async def poll_currently_playing():
    while True:
        try:
            sleep_time = await playback_manager.poll_currently_playing(broadcast_queue_length)
            await asyncio.sleep(sleep_time)
        except Exception as e:
            print("Error polling currently playing:", e)
            await asyncio.sleep(5)

async def broadcast_queue_length():
    queue_length = client_handler.get_queue_length()
    payload = json.dumps({"queue_length": queue_length})
    targets = list(connected_clients.values())
    print(f"Broadcasting queue length {queue_length} to {len(targets)} clients")

    results = await asyncio.gather(*(safe_send(ws, payload) for ws in targets), return_exceptions=True)
    for ws, result in zip(targets, results):
        if isinstance(result, Exception):
            bad_id = None
            for cid, sock in connected_clients.items():
                if sock is ws:
                    bad_id = cid
                    break
            print(f"Pruning client {bad_id}: {result}")
            if bad_id:
                connected_clients.pop(bad_id, None)


async def safe_send(ws, payload):
    await ws.send(payload)

async def client_connector(websocket):
    connected_clients[websocket.id] = websocket
    currency_manager.register_client(websocket.id)
    try:
        currently_playing = client_handler.clean_currently_playing() or {}
        await websocket.send(json.dumps({
            **currently_playing,
            "queue_length": client_handler.get_queue_length(),
            "tokens": currency_manager.get_balance(websocket.id)
        }))
        await broadcast_queue_length()

        async for raw in websocket:
            message = json.loads(raw)
            response = client_handler.message_handler(message, websocket.id)

            if response.get("status") and message.get("action") == "like_track":
                new_balance = playback_manager.request_reward(len(connected_clients))
                owner_id = playback_manager.current_owner
                if new_balance is not None and owner_id in connected_clients:
                    print("Sending reward to:", owner_id, "clients:", list(connected_clients.keys()))
                    await connected_clients[owner_id].send(json.dumps({"tokens": currency_manager.get_balance(owner_id)}))

            if response.get("status"):
                await broadcast_queue_length()
            await websocket.send(json.dumps(response))

    except Exception as e:
        print("Error in client_connector:", e)
    finally:
        currency_manager.remove_client(websocket.id)
        connected_clients.pop(websocket.id, None)

async def start_websocket_server():
    async with serve(client_connector, "localhost", ports["WEBSOCKET_SERVER_PORT"]):
        print(f"Session started on port {ports['WEBSOCKET_SERVER_PORT']}. Room code: {room_code}")
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