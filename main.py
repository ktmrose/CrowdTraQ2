from websockets.asyncio.server import serve
import asyncio

PORT = 7890

print("Server listening on port " + str(PORT))

async def echo(websocket):
    print("A client connected")
    async for message in websocket:
        print("Received message from client "  + message)
        await websocket.send("Pong: " + message)

async def main():
    async with serve(echo, "localhost", PORT) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())