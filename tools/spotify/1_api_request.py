import requests
from pprint import pprint

token = "BQDhnJYaJ6V9pibWAMmf9RwsJq5DZOK1OIyNNEnEkX1EW3BCAH4K4hX28oMBH7JzlGY-W-75RFA4wnfT81zUiXH2Jxj2KMnNw4bTn3-fWMKhPJXMMf8"

url = 'https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aR7qd6V'

headers = {
    "Authorization": "Bearer " + token
}

response = requests.get(url, headers=headers)

# Print the status code and response data for debugging
print(f"Status Code: {response.status_code}")

print(f"Response Data: {response.json()}")