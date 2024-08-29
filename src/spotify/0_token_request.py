import base64
import requests

# Configuration
CLIENT_ID = 'e3de96010f8a4806afc1d7f1d6a71c02'
CLIENT_SECRET = 'd7fa8619a8024b1e95ea896f307fc281'

# Token URL
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Encode credentials
credentials = f'{CLIENT_ID}:{CLIENT_SECRET}'
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Request access token
payload = {
    'grant_type': 'client_credentials'
}
headers = {
    'Authorization': f'Basic {encoded_credentials}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.post(TOKEN_URL, data=payload, headers=headers)
token_info = response.json()

if 'access_token' in token_info:
    access_token = token_info['access_token']
    #print(f'Access Token: {access_token}')
    with open("spotify_token.txt", "w") as file:
        file.write(access_token)
else:
    print('Failed to get access token.')
