import json
import requests
from requests.exceptions import RequestException
import sys

server_ip, server_port = sys.argv[1], sys.argv[2]
input_json, output_json = sys.argv[3], sys.argv[4]


def load_input_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def save_output_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def send_request(payload, url):
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except RequestException as e:
        return {"status": -1, "msg": str(e)}


def main():
    input_data = load_input_json(input_json)
    url = f"http://{server_ip}:{server_port}/v1/devices/"

    method = input_data["method"]
    payload = input_data["data"]

    response_data = send_request(payload, url + method)
    save_output_json(response_data, output_json)


if __name__ == "__main__":
    main()
