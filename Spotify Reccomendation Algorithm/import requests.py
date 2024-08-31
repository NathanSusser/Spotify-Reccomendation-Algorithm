import requests
from base64 import b64encode

# add client id and secret using spotify API instructions
client_id = 
client_secret = 
message = f"{client_id}:{client_secret}"
message_bytes = message.encode('ascii')
base64_bytes = b64encode(message_bytes)
base64_message = base64_bytes.decode('ascii')

headers = {
    'Authorization' : f"Basic {base64_message}"
}

data = {
    'grant_type' : 'client_credentials'
}

response = requests.post('https://accounts.spotify.com/api/token', headers = headers, data = data)

response_data = response.json()
access_token = response_data['access_token']

print(access_token)