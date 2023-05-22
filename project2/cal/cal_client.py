import asyncio
import websockets
import json
import sys

method_map = {'ADD': 'add', 'SUB': 'subtract', 'MUL': 'multiply', 'DIV': 'divide'}


async def cal_client(url, question_file, answer_file):
    with open(question_file, 'r') as f:
        lines = f.readlines()

    async with websockets.connect(url) as websocket:
        for line in lines:
            id, method, param1, param2 = line.strip().split()
            payload = {
                "jsonrpc": "2.0",
                "method": method_map[method],
                "params": [int(param1), int(param2)],
                "id": int(id),
            }
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            response = json.loads(response)

            # Check if the response contains 'result' key, print error message otherwise.
            if 'result' in response:
                with open(answer_file, 'a') as f:
                    f.write(f"{response['id']} {response['result']}\n")
            else:
                print(
                    f"Error processing request {response['id']}: {response.get('error')}"
                )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 cal_client.py <ws_url> <question_file> <answer_file>")
        exit(1)

    url = sys.argv[1]
    question_file = sys.argv[2]
    answer_file = sys.argv[3]
    asyncio.get_event_loop().run_until_complete(
        cal_client(url, question_file, answer_file)
    )
