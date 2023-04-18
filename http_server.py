import os
import json
import pandas as pd
from sanic import Sanic, response
from sanic.request import Request
from sanic.response import json

app = Sanic("DeviceAPI")

csv_file = "devices.csv"
columns = [
    "id", "name", "type",
    "hardware_model", "hardware_sn",
    "software_version", "software_last_update",
    "nic1_type", "nic1_mac", "nic1_ipv4",
    "nic2_type", "nic2_mac", "nic2_ipv4",
    "state"
]

if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_file, index=False)


def flatten_device(device):
    return {
        **{k: device[k] for k in ("id", "name", "type", "state")},
        **{f"hardware_{k}": v for k, v in device["hardware"].items()},
        **{f"software_{k}": v for k, v in device["software"].items()},
        **{f"nic{i+1}_{k}": v for i, nic in enumerate(device["nic"][:2]) for k, v in nic.items()}
    }

@app.post("/v1/devices/add")
async def add_device(request: Request):
    device = request.json
    df = pd.read_csv(csv_file)

    if device["id"] in df["id"].values:
        return json({"status": 400, "msg": "Device ID already exists."}, status=400)
    
    # Flatten device data
    device = flatten_device(device)

    df = df.append(device, ignore_index=True)
    df.to_csv(csv_file, index=False)

    return json({"status": 200, "msg": "Device added successfully."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
