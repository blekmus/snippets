import requests
import json

def send_sms(message, number):
    url = 'https://api.getshoutout.com/coreservice/messages'

    payload = {
        "source": "ShoutDEMO",
        "destinations": [number],
        "content": {
            "sms": message
        },
        "transports": ['sms']
    }

    headers = {
        "Authorization":
        "Bearer slfkjweorijsldfkjsflkas;fj2389047",
        'content-Type': 'application/json',
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload))

    resp.raise_for_status()

    return resp.json()


send_sms("Hello World", "94771234567")
