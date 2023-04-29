import json
import sys

import pandas as pd
from sanic import Sanic
from sanic.request import Request
from sanic.response import json

server_port = int(sys.argv[1])
db_file = sys.argv[2]

app = Sanic("DeviceAPI")

columns = [
    "id",
    "name",
    "type",
    "hardware_model",
    "hardware_sn",
    "software_version",
    "software_last_update",
    "nic1_type",
    "nic1_mac",
    "nic1_ipv4",
    "nic2_type",
    "nic2_mac",
    "nic2_ipv4",
    "state",
]


# if not os.path.exists(db_file):
#     df = pd.DataFrame(columns=columns)
#     df.to_csv(db_file, index=False)


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


@app.post("/v1/devices/ADD")
async def add_device(request: Request):
    devices = request.json
    df = pd.read_csv(db_file)

    for device in devices:
        if device["id"] in df["id"].values:
            return json(
                {"status": 400, "msg": f"Device ID {device['id']} already exists."},
                status=400,
            )

        flat_device = flatten_device(device)
        df = df.append(flat_device, ignore_index=True)

    df.to_csv(db_file, index=False)
    return json({"status": "success", "data": None})


@app.post("/v1/devices/DELETE")
async def delete_device(request: Request):
    device_ids = request.json
    df = pd.read_csv(db_file)

    df = df[~df["id"].isin(device_ids)]
    df.to_csv(db_file, index=False)

    return json({"status": "success", "data": None})


@app.post("/v1/devices/QUERY")
async def query_device(request: Request):
    device_ids = request.json
    df = pd.read_csv(db_file)

    queried_devices = df[df["id"].isin(device_ids)].to_dict(orient='records')

    return json({"status": "success", "data": queried_devices})


@app.post("/v1/devices/QUERYALL")
async def query_all_devices(request: Request):
    df = pd.read_csv(db_file)
    all_devices = df.to_dict(orient='records')
    return json({"status": "success", "data": all_devices})


if __name__ == "__main__":
    app.run(host="localhost", port=server_port)
