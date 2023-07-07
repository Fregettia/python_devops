import json
import aiohttp
import asyncio
import sys
import websockets


def load_input_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


async def main():
    domain_name, device_id, device_password = sys.argv[1:4]

    # Get token
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'http://{domain_name}/auth',
            json={'device_id': device_id, 'device_password': device_password},
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
    # Replace the WebSocket connection code with HTTP POST request to send JSON data
    async with aiohttp.ClientSession() as session:
        while True:
            line = input()
            if line == 'exit':
                break

            data = load_input_json(
                r"C:\Users\yegvo\Documents\python_project\python_devops\final\io\data.json"
            )

            async with session.post(
                f'http://{domain_name}/log',
                json={'auth': token, 'data': data},
            ) as resp:
                result = await resp.json()
                if result['status'] == 0:
                    print('Log sent successfully')
                else:
                    print('Failed to send log')


if __name__ == '__main__':
    asyncio.run(main())
