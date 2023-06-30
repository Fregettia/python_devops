from sanic import Sanic, response
from sanic.exceptions import Unauthorized
import aiomysql
import bcrypt
import jwt

app = Sanic(__name__)

pool = None
secret_key = "your_secret_key"  # Replace with your own secret key


@app.before_server_start
async def init_mysql(app, loop):
    global pool
    pool = await aiomysql.create_pool(
        host="100.68.39.99",
        port=3306,
        user="root",
        password="7JpXnn7Prvrznfr5",
        db='devops',
        loop=loop,
    )


async def check_auth(device_id, device_password):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT secret FROM device WHERE id=%s", (device_id,))
            result = await cur.fetchone()
            if result is None:
                return False
            hashed_password = result[0].encode('utf-8')  # Ensure the password is bytes
            return bcrypt.checkpw(device_password.encode('utf-8'), hashed_password)


def generate_token(device_id):
    payload = {'device_id': device_id}
    return jwt.encode(payload, secret_key, algorithm='HS256')


def validate_token(token):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        device_id = payload['device_id']
        return device_id
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None


@app.post('/auth')
async def auth(request):
    device_id = request.json.get('device_id')
    device_password = request.json.get('device_password')

    if await check_auth(device_id, device_password):
        token = generate_token(device_id)
        return response.json({'status': 0, 'msg': 'ok', 'token': token})
    else:
        return response.json({'status': -1, 'msg': 'fail'})


@app.websocket('/echo')
async def echo(request, ws):
    token = request.args.get('auth')
    device_id = validate_token(token)
    if device_id is None:
        raise Unauthorized("Invalid token")

    while True:
        data = await ws.recv()
        await ws.send(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30000)
