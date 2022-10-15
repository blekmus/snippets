import requests
import json


def send_mail(email, name):
    url = 'https://api.mailersend.com/v1/email'

    with open('mail.html', 'r') as file:
        html = file.read()

    payload = {
        "from": {
            "email": "contactus@aceacademy.lk",
            "name": "Ace Academy"
        },
        "to": [{
            "email": email,
            "name": name,
        }],
        "subject": "2024 Combined Maths Class Starting Shortly",
        "html": html,
        "variables": [{
            "email": email,
            "substitutions": [{
                "var": "name",
                "value": name,
            }]
        }]
    }

    headers = {
        "Authorization": "Bearer AHqdHGTNo-6ufXxwbTeM7p1fuZJ7A",
        'content-Type': 'application/json',
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload))

    resp.raise_for_status()

    return resp.json()


send_mail('some@example.com', 'Some Name')
