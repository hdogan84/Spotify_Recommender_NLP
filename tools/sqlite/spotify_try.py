import requests
import base64
import os
from dotenv import load_dotenv
import json

# .env dosyasındaki CLIENT_ID ve CLIENT_SECRET'i yüklemek için
load_dotenv()

# Spotify API erişimi için gerekli bilgileri al
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# 1. OAuth Token alımı
auth_url = 'https://accounts.spotify.com/api/token'
auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode('utf-8')

response = requests.post(auth_url, headers={
    'Authorization': f'Basic {auth_header}',
    'Content-Type': 'application/x-www-form-urlencoded'
}, data={'grant_type': 'client_credentials'})

token = response.json().get('access_token')

# Sanatçı bilgilerini getiren fonksiyon
def get_artist_genres(artist_id):
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    artist_response = requests.get(artist_url, headers={
        'Authorization': f'Bearer {token}'
    })
    artist_data = artist_response.json()
    return artist_data.get('genres', ['Unknown'])

# 2. Spotify'dan Top 50 Global Playlist'i al
playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Top 50 Global playlist ID
playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

playlist_response = requests.get(playlist_url, headers={
    'Authorization': f'Bearer {token}'
})

tracks = playlist_response.json()['items']

# 3. Sadece bir şarkının ilgili alanlarını yazdır
if tracks:
    track = tracks[0]['track']  # Listedeki ilk şarkıyı al

    # Şarkı bilgileri
    track_name = track.get('name')
    artist_name = track['artists'][0].get('name')  # İlk sanatçının adı
    album_name = track['album'].get('name')
    release_date = track['album'].get('release_date')

    # Ek alanlar
    album_type = track['album'].get('album_type')
    total_tracks = track['album'].get('total_tracks')
    artist_id = track['artists'][0].get('id')
    artist_uri = track['artists'][0].get('uri')
    duration_ms = track.get('duration_ms')
    popularity = track.get('popularity')
    explicit = track.get('explicit')
    preview_url = track.get('preview_url')
    track_number = track.get('track_number')
    external_ids = track['external_ids'].get('isrc')

    # Sanatçının tür bilgisini alalım
    genres = get_artist_genres(artist_id)

    # Yazdırma
    print(f"--------------------------------------------------")
    print(f"Sample Track Informations Return From Spotify API:")
    print(f"--------------------------------------------------")
    print(f"Track Name: {track_name}")
    print(f"Artist Name: {artist_name}")
    print(f"Album Name: {album_name}")
    print(f"Release Date: {release_date}")
    
    print(f"Album Type: {album_type}")
    print(f"Total Tracks in Album: {total_tracks}")
    print(f"Artist ID: {artist_id}")
    print(f"Artist URI: {artist_uri}")
    print(f"Duration (ms): {duration_ms}")
    print(f"Popularity: {popularity}") 
    # Yeni eklenen: Sanatçı türü bilgisi
    print(f"Genres: {genres}")
else:
    print("No tracks found.")
