from sanic import Sanic
from sanic.response import json

app = Sanic(__name__)


@app.websocket('/echo')
async def echo(request, ws):
    while True:
        data = await ws.recv()
        await ws.send(data)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 echo_server.py <port>")
        exit(1)

    port = int(sys.argv[1])
    app.run(host="0.0.0.0", port=port)
