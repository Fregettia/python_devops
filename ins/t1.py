import json
import bcrypt
import pymysql


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


def load_input_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def json2sql(input_file, cursor):
    input_json = load_input_json(input_file)
    method = input_json["method"]
    input_data = input_json["data"]

    if method == 'ADD':
        for device in input_data:
            flat_device = flatten_device(device)
            columns = ', '.join(flat_device.keys())
            values = ', '.join(['%s'] * len(flat_device))
            sql = f"INSERT INTO device ({columns}) VALUES ({values})"
            cursor.execute(sql, tuple(flat_device.values()))
    elif method == "UPDATE":
        for device in input_data:
            flat_device = flatten_device(device)
            sql = "UPDATE device SET "
            sql += ", ".join([f"{k} = %s" for k in flat_device.keys()])
            sql += f" WHERE id = {device['id']}"
            cursor.execute(sql, tuple(flat_device.values()))
    elif method == "DELETE":
        for id in input_data:
            sql = f"DELETE FROM device WHERE id = {id}"
            cursor.execute(sql)
    elif method == "QUERY":
        for id in input_data:
            sql = f"SELECT * FROM device WHERE id = {id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    elif method == "QUERYALL":
        sql = "SELECT * FROM device"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

    elif method == "QUERY_DEVICE_GROUP":
        for id in input_data:
            sql = f"SELECT device.*, device_group.* FROM device JOIN device_group_membership ON device.id = device_group_membership.device_id JOIN device_group ON device_group_membership.group_id = device_group.group_id WHERE device.id = {id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    elif method == "QUERY_ALL_DEVICE_GROUP":
        sql = "SELECT device.*, device_group.* FROM device JOIN device_group_membership ON device.id = device_group_membership.device_id JOIN device_group ON device_group_membership.group_id = device_group.group_id"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
    elif method == "ADD_GROUP":
        for group in input_data:
            columns = ', '.join(group.keys())
            values = ', '.join(['%s'] * len(group))
            sql = f"INSERT INTO device_group ({columns}) VALUES ({values})"
            cursor.execute(sql, tuple(group.values()))
    elif method == "DELETE_GROUP":
        for id in input_data:
            sql = f"DELETE FROM device_group_membership WHERE group_id = {id}"
            cursor.execute(sql)
            sql = f"DELETE FROM device_group WHERE group_id = {id}"
            cursor.execute(sql)
    elif method == "QUERY_GROUP":
        for id in input_data:
            sql = f"SELECT * FROM device_group WHERE group_id = {id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    elif method == "UPDATE_GROUP":
        for group in input_data:
            set_clause = ', '.join([f"{key} = %s" for key in group.keys()])
            sql = f"UPDATE device_group SET {set_clause} WHERE group_id = %s"
            cursor.execute(sql, tuple(group.values()) + (group['group_id'],))
    elif method == "QUERY_ALL_GROUPS":
        sql = "SELECT * FROM device_group"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

    elif method == "ADD_DEVICE_GROUP_RELATIONSHIP":
        for relationship in input_data:
            sql = f"INSERT INTO device_group_membership (device_id, group_id) VALUES (%s, %s)"
            cursor.execute(sql, (relationship['device_id'], relationship['group_id']))
    elif method == "DELETE_DEVICE_GROUP_RELATIONSHIP":
        for relationship in input_data:
            sql = f"DELETE FROM device_group_membership WHERE device_id = %s AND group_id = %s"
            cursor.execute(sql, (relationship['device_id'], relationship['group_id']))
    elif method == "QUERY_DEVICE_BY_GROUP":
        for group_id in input_data:
            sql = f"SELECT device.* FROM device JOIN device_group_membership ON device.id = device_group_membership.device_id WHERE device_group_membership.group_id = {group_id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    elif method == "QUERY_GROUPS_BY_DEVICE":
        for device_id in input_data:
            sql = f"SELECT device_group.* FROM device_group JOIN device_group_membership ON device_group.group_id = device_group_membership.group_id WHERE device_group_membership.device_id = {device_id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    elif method == "DELETE_GROUPS_BY_DEVICE":
        for device_id in input_data:
            sql = f"DELETE FROM device_group_membership WHERE device_id = {device_id}"
            cursor.execute(sql)

    mydb.commit()


if __name__ == "__main__":
    mydb = pymysql.connect(
        host="100.68.39.99", user="root", password="7JpXnn7Prvrznfr5", database="devops"
    )
    mycursor = mydb.cursor()

    json2sql(
        r"final\io\add_r.json",
        mycursor,
    )
