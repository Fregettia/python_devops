from sanic import Sanic, response
from sanic.exceptions import Unauthorized

app = Sanic(__name__)

# Load passwords and tokens
with open('passwd.txt') as f:
    info = [line.strip().split(':') for line in f]
    auth_info = {line[0]: line[1] for line in info}
    token_info = {line[0]: line[2] for line in info}


@app.post('/auth')
async def auth(request):
    username = request.json.get('username')
    password = request.json.get('password')

    if username in auth_info and auth_info[username] == password:
        return response.json({'status': 0, 'msg': 'ok', 'token': token_info[username]})
    else:
        return response.json({'status': -1, 'msg': 'fail'})


@app.websocket('/echo')
async def echo(request, ws):
    if request.args.get('auth') not in token_info.values():
        raise Unauthorized("Invalid token")
    while True:
        data = await ws.recv()
        await ws.send(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30000)
