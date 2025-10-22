from websockets.asyncio.server import serve
import asyncio, json, signal, time

from app.core.init_app import generate_room_code, start_spotify_client, establish_spotify_connection
from app.config.settings import ports
from app.services.currency_manager import CurrencyManager
from app.services.playback_manager import PlaybackManager
from app.handlers.client_handler import ClientHandler
from app.services.identity_manager import IdentityManager

room_code = generate_room_code(4)
shutdown_event = asyncio.Event()
connected_clients = {}

currency_manager = CurrencyManager()
client_handler = ClientHandler(currency_manager)
identity_manager = IdentityManager()

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
    raw = await websocket.recv()
    hello = json.loads(raw)
    session_id = identity_manager.register(websocket, hello.get("sessionId"))

    currency_manager.register_client(session_id)
    try:
        currently_playing = client_handler.clean_currently_playing()
        init_tokens = currency_manager.get_balance(session_id)
        client_vote = client_handler.song_feedback.get_vote(session_id)
        init_payload = {
            "sessionId": session_id,
            **currently_playing,
            "queue_length": client_handler.get_queue_length(),
            "cost": currency_manager.calculate_cost(client_handler.get_queue_length()),
            "tokens": init_tokens,
            "client_vote": client_vote
        }
        await websocket.send(json.dumps(init_payload))

        async for raw in websocket:
            message = json.loads(raw)
            response = client_handler.message_handler(message, session_id)

            if response.get("success"):
                event = await playback_manager.handle_feedback(
                    message.get("action"),
                    len(identity_manager.all_session_ids()),
                    broadcast_queue_length
                )
                if event:
                    await identity_manager.broadcast(event)

                ql = client_handler.get_queue_length()
                await identity_manager.broadcast({"queue_length": ql, "cost": currency_manager.calculate_cost(ql)})

            await websocket.send(json.dumps(response))

    except Exception as e:
        print("Error in client_connector:", e)
    finally:
        currency_manager.remove_client(session_id)
        identity_manager.unregister(session_id)

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
        elapsed = shutdown_end - shutdown_start
        minutes, seconds = divmod(int(elapsed), 60)
        print(f"Shutdown took {minutes}m {seconds}s.")


def handle_exit(signum, frame):
    print("Caught termination signal. Shutting down...")
    shutdown_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    asyncio.run(main())