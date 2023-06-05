import json
import pymysql


def load_input_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def flatten_device(device):
    return {
        **{k: device[k] for k in ("id", "name", "type", "state")},
        **{f"hardware_{k}": v for k, v in device["hardware"].items()},
        **{f"software_{k}": v for k, v in device["software"].items()},
        **{
            f"nic{i + 1}_{k}": v
            for i, nic in enumerate(device["nic"][:2])
            for k, v in nic.items()
        },
    }


def json2sql(input_file, cursor):
    input_json = load_input_json(input_file)
    method = input_json["method"]
    test_devices = input_json["data"]

    if method == 'ADD':
        for device in test_devices:
            flat_device = flatten_device(device)
            columns = ', '.join(flat_device.keys())
            values = ', '.join(['%s'] * len(flat_device))
            sql = f"INSERT INTO device ({columns}) VALUES ({values})"
            cursor.execute(sql, tuple(flat_device.values()))
    elif method == "DELETE":
        for id in test_devices:
            sql = f"DELETE FROM device WHERE id = {id}"
            cursor.execute(sql)
    elif method == "QUERY":
        for id in test_devices:
            sql = f"SELECT * FROM device WHERE id = {id}"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    elif method == "QUERYALL":
        sql = "SELECT * FROM device"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

    mydb.commit()


if __name__ == "__main__":
    mydb = pymysql.connect(
        host="100.68.39.99", user="root", password="7JpXnn7Prvrznfr5", database="devops"
    )
    mycursor = mydb.cursor()

    json2sql(
        r"C:\Users\yegvo\Documents\python_project\python_devops\project3\query.json",
        mycursor,
    )

    # mycursor.execute("SELECT * FROM device")
    # myresult = mycursor.fetchall()
    # for x in myresult:
    #     print(x)
