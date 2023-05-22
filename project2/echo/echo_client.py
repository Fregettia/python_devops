import asyncio
import websockets
import sys


async def echo_client(url):
    async with websockets.connect(url) as websocket:
        while True:
            message = input("$ ")
            if message == 'exit':
                break
            await websocket.send(message)
            response = await websocket.recv()
            print(response)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 echo_client.py <ws_url>")
        exit(1)

    url = sys.argv[1]
    asyncio.get_event_loop().run_until_complete(echo_client(url))
