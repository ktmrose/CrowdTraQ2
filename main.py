from websockets.asyncio.server import serve
import asyncio
from init import generate_room_code, establish_spotify_connection
import json
from config import ports
from routes import app
from threading import Thread

# requests library or httpx library

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
        try: 
            await server.serve_forever() 
        except asyncio.CancelledError: 
            print("Shutting down WebSocket server...")

def start_spotify_client():
    print("Starting Spotify client on port " + str(ports["SPOTIFY_CLIENT_PORT"]))
    app.run(port=ports["SPOTIFY_CLIENT_PORT"])
    establish_spotify_connection()

async def main():

    spotify_client_thread = Thread(target=start_spotify_client)
    spotify_client_thread.start()

    try:
        await start_websocket_server()
    except KeyboardInterrupt:
        print("Manual kill commanded, shutting down servers...")
    finally:
        print("Cleaning up tasks...")
        current_task = asyncio.current_task()
        tasks = [task for task in asyncio.all_tasks() if task is not current_task and not task.done()]
        for task in tasks:
            task.cancel()
        print(f"Cancelled {len(tasks)} tasks.")
        await asyncio.gather(*tasks, return_exceptions=True) 

        spotify_client_thread.join()
        print("Servers successfully shut down")


if __name__ == "__main__":
    asyncio.run(main())