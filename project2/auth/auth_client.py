import aiohttp
import asyncio
import sys
import websockets


async def main():
    domain_name, username, password = sys.argv[1:4]

    # Get token
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'http://{domain_name}/auth',
            json={'username': username, 'password': password},
        ) as resp:
            data = await resp.json()
            if data['status'] == -1:
                print('login fail')
                sys.exit()
            token = data.get('token', '')
            if not token:
                print('Token not received')
                sys.exit()
            print(token)

    # Connect to websocket
    async with websockets.connect(f'ws://{domain_name}/echo?auth={token}') as ws:
        while True:
            line = input()
            if line == 'exit':
                break
            await ws.send(line)
            print(await ws.recv())


if __name__ == '__main__':
    asyncio.run(main())