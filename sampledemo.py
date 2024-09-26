import os
import requests
from flask import Flask
import asyncio
from aiohttp import ClientSession


app = Flask(__name__)

# Salesforce credentials (should ideally be in environment variables)
CLIENT_ID = os.getenv('SALESFORCE_CLIENT_ID')
CLIENT_SECRET = os.getenv('SALESFORCE_CLIENT_SECRET')
USERNAME = os.getenv('SALESFORCE_USERNAME')
PASSWORD = os.getenv('SALESFORCE_PASSWORD')
TOKEN_URL = 'https://login.salesforce.com/services/oauth2/token'
ACCESS_TOKEN = ''
INSTANCE_URL = ''


# Authenticate and get access token
def get_access_token():
    global ACCESS_TOKEN, INSTANCE_URL
    data = {
        'grant_type': 'password',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'username': USERNAME,
        'password': PASSWORD
    }

    response = requests.post(TOKEN_URL, data=data)

    if response.status_code == 200:
        resp_json = response.json()
        ACCESS_TOKEN = resp_json['access_token']
        INSTANCE_URL = resp_json['instance_url']
    else:
        raise Exception(f"Failed to authenticate: {response.content}")


async def subscribe_to_event():
    # Create a session and a WebSocket connection
    async with ClientSession() as session:
        async with session.ws_connect(f"{INSTANCE_URL}/cometd/57.0") as ws:
            # Handshake
            handshake = {
                "channel": "/meta/handshake",
                "version": "1.0",
                "minimumVersion": "1.0",
                "clientId": ACCESS_TOKEN,
            }
            await ws.send_json(handshake)
            response = await ws.receive()
            print(f"Handshake response: {response.data}")

            # Subscribe to the platform event
            subscribe_message = {
                "channel": "/meta/subscribe",
                "clientId": ACCESS_TOKEN,
                "subscription": "/event/DemoEvent__e"
            }
            await ws.send_json(subscribe_message)
            response = await ws.receive()
            print(f"Subscription response: {response.data}")

            # Listen for events
            while True:
                event_response = await ws.receive()
                print(f"Received event: {event_response.data}")


@app.route('/')
def index():
    try:
        get_access_token()  # Authenticate to get the access token
        asyncio.run(subscribe_to_event())  # Subscribe to the event
        return "Subscribed to platform events.", 200
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
