import json
import requests
from requests.exceptions import RequestException

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
    input_data = load_input_json("input.json")
    url = "http://<ip>:8000/v1/devices/add"

    payload = input_data["data"]

    response_data = send_request(payload, url)
    save_output_json(response_data, "output.json")

if __name__ == "__main__":
    main()
