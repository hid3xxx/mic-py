import asyncio
import websockets


async def handle_client(websocket):
    while True:
        try:
            message = await websocket.recv()
            print(f"Received message: {message}")
        except websockets.ConnectionClosed:
            print("connection closed")
            break


async def main():
    server = await websockets.serve(handle_client, "localhost", 8000)
    print("WebSocket server is running on ws://localhost:8000/ws")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
