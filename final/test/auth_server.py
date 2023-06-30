from sanic import Sanic, response
from sanic.exceptions import Unauthorized
import aiomysql
import bcrypt

app = Sanic(__name__)

pool = None

@app.before_server_start
async def init_mysql(app, loop):
    global pool
    pool = await aiomysql.create_pool(host="100.68.39.99", port=3306,
                                      user="root", password="7JpXnn7Prvrznfr5", 
                                      db='devops', loop=loop)

async def check_auth(device_id, device_password):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT password FROM device WHERE id=%s", (device_id,))
            result = await cur.fetchone()
            if result is None:
                return False
            hashed_password = result[0].encode('utf-8')  # Ensure the password is bytes
            return bcrypt.checkpw(device_password.encode('utf-8'), hashed_password)

@app.post('/auth')
async def auth(request):
    device_id = request.json.get('device_id')
    device_password = request.json.get('device_password')

    if await check_auth(device_id, device_password):
        return response.json({'status': 0, 'msg': 'ok', 'token': device_id})  # Token is just the device_id here
    else:
        return response.json({'status': -1, 'msg': 'fail'})

@app.websocket('/echo')
async def echo(request, ws):
    token = request.args.get('auth')
    if token is None or not await check_auth(token, ''):
        raise Unauthorized("Invalid token")
    while True:
        data = await ws.recv()
        await ws.send(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30000)
