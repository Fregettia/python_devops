from sanic import Sanic
from jsonrpcserver import method, async_dispatch, Success

app = Sanic(__name__)


@method
async def add(param1, param2):
    return Success(param1 + param2)


@method
async def subtract(param1, param2):
    return Success(param1 - param2)


@method
async def multiply(param1, param2):
    return Success(param1 * param2)


@method
async def divide(param1, param2):
    return Success(param1 / param2)


@app.websocket('/cal')
async def cal(request, ws):
    while True:
        request = await ws.recv()
        response = await async_dispatch(request)
        await ws.send(str(response))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 cal_server.py <port>")
        exit(1)

    port = int(sys.argv[1])
    app.run(host="0.0.0.0", port=port)
