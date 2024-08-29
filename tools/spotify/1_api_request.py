import requests
from pprint import pprint


with open('spotify_token.txt', 'r') as file:
    # Read the contents of the file and store it in a variable
    token = file.read()

url = 'https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aR7qd6V'

headers = {
    "Authorization": "Bearer " + token
}

response = requests.get(url, headers=headers)

# Print the status code and response data for debugging
print(f"Status Code: {response.status_code}")

print(f"Response Data: {response.json()}")