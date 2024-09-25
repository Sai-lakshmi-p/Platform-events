import requests
from flask import Flask

app = Flask(__name__)

# Salesforce credentials
CLIENT_ID = (
    '3MVG9fe4g9fhX0E4eEi0k1.NeeMFJ934LpNVtnq4dQtwHMxO2aqtvxl'
    '0rmQleyR_Dr2tQRUriZIBH84IRVakt'
)
CLIENT_SECRET = (
    '27D317E58AB814ABABAB8A1748FD6915A93034BEF3733E17403C439'
    '3AB2FC2C3'
)
USERNAME = 'sailakshmi@salesforce.com'
PASSWORD = 'Welcome$2024'
TOKEN_URL = 'https://login.salesforce.com/services/oauth2/token'
INSTANCE_URL = ''
ACCESS_TOKEN = 'QqtNVG1L466zl4fJqnQmUm2Z'


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


# Subscribe to platform event
def subscribe_to_event():
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    event_subscription_url = (f'{INSTANCE_URL}/services/data/v57.0/'
                              'event/DemoEvent__e')

    response = requests.get(event_subscription_url, headers=headers)

    if response.status_code == 200:
        print(f"Subscribed to Platform Event. Data received: "
              f"{response.json()}")
        return response.json()
    else:
        print(f"Failed to subscribe: {response.content}")
        return None


@app.route('/')
def index():
    try:
        get_access_token()  # Authenticate to get the access token
        events = subscribe_to_event()  # Subscribe to the event
        return f"Subscribed and received event data: {events}", 200
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
