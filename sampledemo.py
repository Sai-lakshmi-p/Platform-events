import os
import requests
import json


# Salesforce configuration
SALESFORCE_INSTANCE_URL = 'https://your_instance.salesforce.com'
SALESFORCE_CLIENT_ID = os.getenv('SALESFORCE_CLIENT_ID')
SALESFORCE_CLIENT_SECRET = os.getenv('SALESFORCE_CLIENT_SECRET')
SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME')
SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD')


# Get access token
def get_access_token():
    url = f'{SALESFORCE_INSTANCE_URL}/services/oauth2/token'
    payload = {
        'grant_type': 'password',
        'client_id': SALESFORCE_CLIENT_ID,
        'client_secret': SALESFORCE_CLIENT_SECRET,
        'username': SALESFORCE_USERNAME,
        'password': SALESFORCE_PASSWORD
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print('Error obtaining access token:', response.json())
        return None


# Subscribe to the platform event
def subscribe_to_platform_event(access_token):
    channel = '/event/DemoEvent__e'  
    url = f'{SALESFORCE_INSTANCE_URL}/services/channel/{channel}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Create a long polling connection to receive events
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        print('Subscribed to platform event. Waiting for events...')

        for line in response.iter_lines():
            if line:
                event = json.loads(line.decode('utf-8'))
                print('Received event:', json.dumps(event, indent=4))
    else:
        print('Error subscribing to platform event:', response.json())


if __name__ == "__main__":
    access_token = get_access_token()

    if access_token:
        subscribe_to_platform_event(access_token)
    else:
        print('Failed to obtain access token.')
