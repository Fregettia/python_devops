import bcrypt
import pymysql
import pytest
from sanic import Sanic, response
from sanic import Sanic
from sanic_testing import TestManager
from sanic.request import Request
from sanic.response import json
import json as jsonlib

mydb = pymysql.connect(
    host="100.68.39.99", user="root", password="7JpXnn7Prvrznfr5", database="devops"
)
mycursor = mydb.cursor()


def load_input_json(filename):
    with open(filename, "r") as f:
        return jsonlib.load(f)


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


@pytest.fixture
def sanic_app():
    app = Sanic("TestSanic")
    TestManager(app)

    @app.post("/v1/devices/<operation>")
    async def process_device(request: Request, operation: str):
        input_data = request.json

        if operation in [
            'CREATE_DEVICE',
            'DELETE_DEVICE',
            'UPDATE_DEVICE',
            'QUERY_DEVICE',
            'QUERY_ALL_DEVICE',
        ]:
            if operation == 'CREATE_DEVICE':
                for device in input_data:
                    flat_device = flatten_device(device)
                    columns = ', '.join(flat_device.keys())
                    values = ', '.join(['%s'] * len(flat_device))
                    sql = f"INSERT INTO device ({columns}) VALUES ({values})"
                    mycursor.execute(sql, tuple(flat_device.values()))
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'DELETE_DEVICE':
                for id in input_data:
                    sql = f"DELETE FROM device WHERE id = {id}"
                    mycursor.execute(sql)
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'UPDATE_DEVICE':
                for device in input_data:
                    flat_device = flatten_device(device)
                    sql = "UPDATE device SET "
                    sql += ", ".join([f"{k} = %s" for k in flat_device.keys()])
                    sql += f" WHERE id = {device['id']}"
                    mycursor.execute(sql, tuple(flat_device.values()))
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'QUERY_DEVICE':
                for id in input_data:
                    sql = f"SELECT * FROM device WHERE id = {id}"
                    mycursor.execute(sql)
                    myresult = mycursor.fetchall()
                    return json({"status": "success", "data": str(myresult)})
            elif operation == 'QUERY_ALL_DEVICE':
                sql = "SELECT * FROM device"
                mycursor.execute(sql)
                myresult = mycursor.fetchall()
                return json({"status": "success", "data": myresult})

        if operation in [
            'CREATE_GROUP',
            'DELETE_GROUP',
            'UPDATE_GROUP',
            'QUERY_GROUP',
            'QUERY_ALL_GROUP',
        ]:
            if operation == 'CREATE_GROUP':
                for group in input_data:
                    sql = "INSERT INTO device_group ("
                    sql += ", ".join(group.keys())
                    sql += ") VALUES ("
                    sql += ", ".join(['%s'] * len(group))
                    sql += ")"
                    mycursor.execute(sql, tuple(group.values()))
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'DELETE_GROUP':
                for group_id in input_data:
                    sql = f"DELETE FROM device_group WHERE group_id = {group_id}"
                    mycursor.execute(sql)
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'UPDATE_GROUP':
                for group in input_data:
                    sql = "UPDATE device_group SET "
                    sql += ", ".join([f"{k} = %s" for k in group.keys()])
                    sql += f" WHERE group_id = {group['group_id']}"
                    mycursor.execute(sql, tuple(group.values()))
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'QUERY_GROUP':
                for group_id in input_data:
                    sql = f"SELECT * FROM device_group WHERE group_id = {group_id}"
                    mycursor.execute(sql)
                    myresult = mycursor.fetchall()
                    return json({"status": "success", "data": myresult})
            elif operation == 'QUERY_ALL_GROUP':
                sql = "SELECT * FROM device_group"
                mycursor.execute(sql)
                myresult = mycursor.fetchall()
                return json({"status": "success", "data": myresult})

        if operation in [
            'ADD_DEVICE_GROUP_RELATIONSHIP',
            'DELETE_DEVICE_GROUP_RELATIONSHIP',
            'QUERY_DEVICE_AND_GROUP',
            'QUERY_GROUP_BY_DEVICE',
            'DELETE_GROUP_BY_DEVICE',
            'QUERY_DEVICE_BY_GROUP',
            'QUERY_ALL_DEVICE_AND_GROUP',
        ]:
            if operation == 'ADD_DEVICE_GROUP_RELATIONSHIP':
                for relationship in input_data:
                    columns = ', '.join(relationship.keys())
                    values = ', '.join(['%s'] * len(relationship))
                    sql = f"INSERT INTO device_group_membership ({columns}) VALUES ({values})"
                    mycursor.execute(sql, tuple(relationship.values()))
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'DELETE_DEVICE_GROUP_RELATIONSHIP':
                for relationship in input_data:
                    group_id = relationship['group_id']
                    device_id = relationship['device_id']
                    sql = "DELETE FROM device_group_membership WHERE group_id = %s AND device_id = %s"
                    val = (group_id, device_id)
                    mycursor.execute(sql, val)
                mydb.commit()
                return json({"status": "success", "data": None})

            elif operation == 'QUERY_DEVICE_AND_GROUP':
                for device_id in input_data:
                    sql = f"SELECT device_group.* FROM device_group JOIN device_group_membership ON device_group.group_id = device_group_membership.group_id WHERE device_group_membership.device_id = {device_id}"
                    mycursor.execute(sql)
                    result = mycursor.fetchall()
                return json({"status": "success", "data": result})
            elif operation == 'QUERY_GROUP_BY_DEVICE':
                for device_id in input_data:
                    sql = f"SELECT device_group.* FROM device_group JOIN device_group_membership ON device_group.group_id = device_group_membership.group_id WHERE device_group_membership.device_id = {device_id}"
                    mycursor.execute(sql)
                    result = mycursor.fetchall()
                return json({"status": "success", "data": result})
            elif operation == 'DELETE_GROUP_BY_DEVICE':
                for device_id in input_data:
                    sql = f"DELETE FROM device_group_membership WHERE device_id = {device_id}"
                    mycursor.execute(sql)
                mydb.commit()
                return json({"status": "success", "data": None})
            elif operation == 'QUERY_DEVICE_BY_GROUP':
                for group_id in input_data:
                    sql = f"SELECT device.* FROM device JOIN device_group_membership ON device.id = device_group_membership.device_id WHERE device_group_membership.group_id = {group_id}"
                    mycursor.execute(sql)
                    result = mycursor.fetchall()
                return json({"status": "success", "data": str(result)})
            elif operation == 'QUERY_ALL_DEVICE_AND_GROUP':
                sql = "SELECT * FROM device_group_membership"
                mycursor.execute(sql)
                result = mycursor.fetchall()
                return json({"status": "success", "data": str(result)})

    return app


# 创建一个设备，然后检查数据库中是否存在该设备
def test_create_device(sanic_app):
    input_data = load_input_json(r"io\device\add.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/CREATE_DEVICE", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    device_id = input_data['data'][0]['id']
    sql = f"SELECT * FROM device WHERE id = {device_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult[0][0] == device_id


# 查询刚刚创建的设备，检查返回的设备信息是否正确
def test_query_device(sanic_app):
    input_data = load_input_json(r"io\device\query.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/QUERY_DEVICE", json=input_data['data']
    )
    expected = load_input_json(r"io\device\add.json")['data'][0]
    assert response.status == 200


# 更新设备的一些信息，然后检查数据库中是否更新成功
def test_update_device(sanic_app):
    input_data = load_input_json(r"io\device\update.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/UPDATE_DEVICE", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    device_id = input_data['data'][0]['id']
    sql = f"SELECT * FROM device WHERE id = {device_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult[0][18] == "3"


# 创建一个设备分组，然后检查数据库中是否存在该设备分组
def test_create_group(sanic_app):
    input_data = load_input_json(r"io\group\add.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/CREATE_GROUP", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    group_id = input_data['data'][0]['group_id']
    sql = f"SELECT * FROM device_group WHERE group_id = {group_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult[0][0] == group_id


# 查询刚刚创建的设备分组,检查返回的设备分组信息是否正确
def test_query_group(sanic_app):
    input_data = load_input_json(r"io\group\query.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/QUERY_GROUP", json=input_data['data']
    )
    assert response.status == 200


# 更新设备分组的一些信息，然后检查数据库中是否更新成功
def test_update_group(sanic_app):
    input_data = load_input_json(r"io\group\update.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/UPDATE_GROUP", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    group_id = input_data['data'][0]['group_id']
    sql = f"SELECT * FROM device_group WHERE group_id = {group_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult[0][3] == "2023-06-28 22:15:45"


# 为一个设备添加一个设备分组，然后查询设备和设备分组，看是否显示了新的关系
def test_add_device_group_relationship(sanic_app):
    input_data = load_input_json(r"io\relationship\add.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/ADD_DEVICE_GROUP_RELATIONSHIP", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    device_id = input_data['data'][0]['device_id']
    sql = f"SELECT device_group.* FROM device_group JOIN device_group_membership ON device_group.group_id = device_group_membership.group_id WHERE device_group_membership.device_id = {device_id}"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    assert result[0][0] == 2


# 测试queryDeviceAndGroupById,结果不为空
def test_query_device_and_group(sanic_app):
    input_data = load_input_json(r"io\relationship\query_d_and_g.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/QUERY_DEVICE_AND_GROUP", json=input_data['data']
    )
    assert response.status == 200
    assert response.json != {"status": "success", "data": None}


# 测试queryGroupByDeviceId,结果不为空
def test_query_group_by_device(sanic_app):
    input_data = load_input_json(r"io\relationship\query_g_by_d.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/QUERY_GROUP_BY_DEVICE", json=input_data['data']
    )
    assert response.status == 200
    assert response.json != {"status": "success", "data": None}


# 测试queryDeviceByGroupId
def test_query_device_by_group(sanic_app):
    input_data = load_input_json(r"io\relationship\query_d_by_g.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/QUERY_DEVICE_BY_GROUP", json=input_data['data']
    )
    assert response.status == 200
    assert response.json != {"status": "success", "data": None}


# 测试queryAllDeviceAndGroup
def test_query_all_device_and_group(sanic_app):
    input_data = load_input_json(r"io\relationship\query_all.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/QUERY_ALL_DEVICE_AND_GROUP", json=input_data['data']
    )
    assert response.status == 200


# 测试deleteGroupByDeviceId
def test_delete_group_by_device(sanic_app):
    input_data = load_input_json(r"io\relationship\delete_g_by_d.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/DELETE_GROUP_BY_DEVICE", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    device_id = input_data['data'][0]
    sql = f"SELECT * FROM device_group_membership WHERE device_id = {device_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult == ()


# 删除一个设备和设备分组的关系，然后查询设备和设备分组的关系，看是否不再显示该关系
def test_delete_device_group_relationship(sanic_app):
    input_data = load_input_json(r"io\relationship\delete.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/DELETE_DEVICE_GROUP_RELATIONSHIP", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    group_id = input_data['data'][0]['group_id']
    sql = f"SELECT * FROM device_group_membership WHERE group_id = {group_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult == ()


# 删除设备分组
def test_delete_group(sanic_app):
    input_data = load_input_json(r"io\group\delete.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/DELETE_GROUP", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    group_id = input_data['data'][0]
    sql = f"SELECT * FROM device_group WHERE group_id = {group_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult == ()


# 删除设备，然后检查数据库中是否删除成功
def test_delete_device(sanic_app):
    input_data = load_input_json(r"io\device\delete.json")
    request, response = sanic_app.test_client.post(
        "/v1/devices/DELETE_DEVICE", json=input_data['data']
    )
    assert response.status == 200
    assert response.json == {"status": "success", "data": None}
    device_id = input_data['data'][0]
    sql = f"SELECT * FROM device WHERE id = {device_id}"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    assert myresult == ()
