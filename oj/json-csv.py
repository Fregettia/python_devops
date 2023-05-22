import json
import sys
import csv

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


def load_input_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def json2csv(input_file):
    test_devices = load_input_json(input_file)
    filename = input_file.replace(".json", ".csv")

    with open(filename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        for device in test_devices:
            flat_device = flatten_device(device)
            writer.writerow(flat_device)


def csv2json(input_file):
    filename = input_file.replace(".csv", ".json")
    devices = []

    with open(input_file, "r", newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            flat_device = dict(zip(columns, row))
            expanded_device = expand_device(flat_device)
            devices.append(expanded_device)

    with open(filename, "w") as f:
        json.dump(devices, f)


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


def expand_device(flat_device):
    nic1 = {
        "type": flat_device["nic1_type"],
        "mac": flat_device["nic1_mac"],
        "ipv4": flat_device["nic1_ipv4"],
    }
    nic2 = (
        {
            "type": flat_device["nic2_type"],
            "mac": flat_device["nic2_mac"],
            "ipv4": flat_device["nic2_ipv4"],
        }
        if flat_device["nic2_type"]
        else None
    )

    return {
        "id": flat_device["id"],
        "name": flat_device["name"],
        "type": flat_device["type"],
        "hardware": {
            "model": flat_device["hardware_model"],
            "sn": flat_device["hardware_sn"],
        },
        "software": {
            "version": flat_device["software_version"],
            "last_update": flat_device["software_last_update"],
        },
        "nic": [nic1, nic2] if nic2 else [nic1],
        "state": flat_device["state"],
    }


if __name__ == "__main__":
    option = sys.argv[1]
    input_file = sys.argv[2]

    if option == "-b":
        csv2json(input_file)
    elif option == "-p":
        json2csv(input_file)
    else:
        print("Invalid option.")
