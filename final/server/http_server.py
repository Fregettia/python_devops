import json
import bcrypt
import pymysql
from sanic import Sanic
from sanic.request import Request
from sanic.response import json

app = Sanic("DeviceAPI")

# establish database connection
mydb = pymysql.connect(
    host="100.68.39.99", user="root", password="7JpXnn7Prvrznfr5", database="devops"
)
mycursor = mydb.cursor()


def flatten_device(device):
    hashed = bcrypt.hashpw(device["secret"].encode('utf-8'), bcrypt.gensalt())
    return {
        **{
            k: device[k]
            for k in (
                "id",
                "name",
                "type",
                "state",
                "description",
                "creation_time",
                "update_time",
            )
        },
        "secret": hashed.decode('utf-8'),
        **{f"hardware_{k}": v for k, v in device["hardware"].items()},
        **{f"software_{k}": v for k, v in device["software"].items()},
        **{f"business_software_{k}": v for k, v in device["business_software"].items()},
        **{
            f"nic{i + 1}_{k}": v
            for i, nic in enumerate(device["nic"][:2])
            for k, v in nic.items()
        },
    }


@app.post("/v1/devices/CREATE_DEVICE")
async def create_device(request: Request):
    input_data = request.json
    for device in input_data:
        flat_device = flatten_device(device)
        columns = ', '.join(flat_device.keys())
        values = ', '.join(['%s'] * len(flat_device))
        sql = f"INSERT INTO device ({columns}) VALUES ({values})"
        mycursor.execute(sql, tuple(flat_device.values()))
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/DELETE_DEVICE")
async def delete_device_by_id(request: Request):
    input_data = request.json
    for id in input_data:
        sql = f"DELETE FROM device WHERE id = {id}"
        mycursor.execute(sql)
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/UPDATE_DEVICE")
async def update_device_by_id(request: Request):
    input_data = request.json
    for device in input_data:
        flat_device = flatten_device(device)
        sql = "UPDATE device SET "
        sql += ", ".join([f"{k} = %s" for k in flat_device.keys()])
        sql += f" WHERE id = {device['id']}"
        mycursor.execute(sql, tuple(flat_device.values()))
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/QUERY_DEVICE")
async def query_device_by_id(request: Request):
    input_data = request.json
    for id in input_data:
        sql = f"SELECT * FROM device WHERE id = {id}"
        mycursor.execute(sql)
        result = mycursor.fetchall()
    return json({"status": "success", "data": result})


@app.post("/v1/devices/QUERY_ALL_DEVICE")
async def query_all_devices(request: Request):
    sql = "SELECT * FROM device"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    return json({"status": "success", "data": result})


@app.post("/v1/devices/CREATE_GROUP")
async def create_device_group(request: Request):
    input_data = request.json
    for group in input_data:
        columns = ', '.join(group.keys())
        values = ', '.join(['%s'] * len(group))
        sql = f"INSERT INTO device_group ({columns}) VALUES ({values})"
        mycursor.execute(sql, tuple(group.values()))
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/DELETE_GROUP")
async def delete_group_by_id(request: Request):
    input_data = request.json
    for id in input_data:
        sql = f"DELETE FROM device_group WHERE group_id = {id}"
        mycursor.execute(sql)
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/UPDATE_GROUP")
async def update_group_by_id(request: Request):
    input_data = request.json
    for group in input_data:
        sql = "UPDATE device_group SET "
        sql += ", ".join([f"{k} = %s" for k in group.keys()])
        sql += f" WHERE group_id = {group['group_id']}"
        mycursor.execute(sql, tuple(group.values()))
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/QUERY_GROUP")
async def query_group_by_id(request: Request):
    input_data = request.json
    for id in input_data:
        sql = f"SELECT * FROM device_group WHERE group_id = {id}"
        mycursor.execute(sql)
        result = mycursor.fetchall()
    return json({"status": "success", "data": result})


@app.post("/v1/devices/QUERY_ALL_GROUP")
async def query_all_device_groups(request: Request):
    sql = "SELECT * FROM device_group"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    return json({"status": "success", "data": result})


@app.post("/v1/devices/ADD_DEVICE_GROUP_RELATIONSHIP")
async def add_device_group_relationship(request: Request):
    input_data = request.json
    for relationship in input_data:
        columns = ', '.join(relationship.keys())
        values = ', '.join(['%s'] * len(relationship))
        sql = f"INSERT INTO device_group_membership ({columns}) VALUES ({values})"
        mycursor.execute(sql, tuple(relationship.values()))
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/DELETE_DEVICE_GROUP_RELATIONSHIP")
async def delete_device_group_relationship(request: Request):
    input_data = request.json
    for id in input_data:
        sql = f"DELETE FROM device_group_membership WHERE group_id = {id}"
        mycursor.execute(sql)
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/QUERY_DEVICE_AND_GROUP")
async def query_device_and_group_by_id(request: Request):
    input_data = request.json
    for device_id in input_data:
        sql = f"SELECT device_group.* FROM device_group JOIN device_group_membership ON device_group.group_id = device_group_membership.group_id WHERE device_group_membership.device_id = {device_id}"
        mycursor.execute(sql)
        result = mycursor.fetchall()
    return json({"status": "success", "data": result})


@app.post("/v1/devices/QUERY_GROUP_BY_DEVICE")
async def query_groups_by_device_id(request: Request):
    input_data = request.json
    for device_id in input_data:
        sql = f"SELECT device_group.* FROM device_group JOIN device_group_membership ON device_group.group_id = device_group_membership.group_id WHERE device_group_membership.device_id = {device_id}"
        mycursor.execute(sql)
        result = mycursor.fetchall()
    return json({"status": "success", "data": result})


@app.post("/v1/devices/DELETE_GROUP_BY_DEVICE")
async def delete_groups_by_device_id(request: Request):
    input_data = request.json
    for device_id in input_data:
        sql = f"DELETE FROM device_group_membership WHERE device_id = {device_id}"
        mycursor.execute(sql)
    mydb.commit()
    return json({"status": "success", "data": None})


@app.post("/v1/devices/QUERY_DEVICE_BY_GROUP")
async def query_devices_by_group_id(request: Request):
    input_data = request.json
    for group_id in input_data:
        sql = f"SELECT device.* FROM device JOIN device_group_membership ON device.id = device_group_membership.device_id WHERE device_group_membership.group_id = {group_id}"
        mycursor.execute(sql)
        result = mycursor.fetchall()
    return json({"status": "success", "data": result})


@app.post("/v1/devices/QUERY_ALL_DEVICE_AND_GROUP")
async def query_all_devices_and_groups(request: Request):
    sql = "SELECT * FROM device_group"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    return json({"status": "success", "data": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
