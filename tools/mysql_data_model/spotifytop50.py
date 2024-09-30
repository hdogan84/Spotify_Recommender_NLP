import requests
import base64
import mysql.connector
import os
from datetime import datetime
import pandas as pd

# 1. Client ID - Client Secret
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# 2. OAuth Token
auth_url = 'https://accounts.spotify.com/api/token'
auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode('utf-8')

# read .env
db_config = {
    'user': 'root', 
    'password': os.getenv('MYSQL_ROOT_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE')
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

response = requests.post(auth_url, headers={
    'Authorization': f'Basic {auth_header}',
    'Content-Type': 'application/x-www-form-urlencoded'
}, data={'grant_type': 'client_credentials'})

token = response.json().get('access_token')

# Top 50 Global playlist
playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Top 50 Global playlist ID
playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

playlist_response = requests.get(playlist_url, headers={
    'Authorization': f'Bearer {token}'
})

tracks = playlist_response.json()['items']

# get genre_id
def get_artist_genres(artist_id):
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    artist_response = requests.get(artist_url, headers={
        'Authorization': f'Bearer {token}'
    })
    artist_data = artist_response.json()
    return artist_data.get('genres', ['Unknown'])


# Get Spotify data and insert into tables
def insert_or_get_id(table, id_column, value_column, value):
    query = f"SELECT {id_column} FROM {table} WHERE {value_column} = %s"
    cursor.execute(query, (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    query = f"INSERT INTO {table} ({value_column}) VALUES (%s)"
    cursor.execute(query, (value,))
    #conn.commit()  # Insert işleminden sonra commit
    return cursor.lastrowid

def insert_artist_genres(artist_id_db, genres):
    for genre in genres:
        genre = genre.lower()
        genre_id = insert_or_get_id("Genres", "genre_id", "genre_desc", genre)
        query = """
            INSERT IGNORE INTO Artist_Genres (artist_id, genre_id)
            VALUES (%s, %s)
        """
        cursor.execute(query, (artist_id_db, genre_id))
    #conn.commit()

for track in tracks:
    track_name = track['track']['name'].strip().lower()
    artist_name = track['track']['artists'][0]['name'].strip().lower()
    artist_id = track['track']['artists'][0]['id']
    release_date = track['track']['album']['release_date']
    

    if len(release_date) == 4:
        formatted_release_date = pd.to_datetime(release_date, format='%Y', errors='coerce').strftime('%Y-%m-%d')
    else:
        formatted_release_date = pd.to_datetime(release_date, errors='coerce').strftime('%Y-%m-%d')
    
    
    # artist-genres information
    genres = get_artist_genres(artist_id)
    
    # inserts
    artist_id_db = insert_or_get_id("Artists", "artist_id", "artist_name", artist_name)
    insert_artist_genres(artist_id_db, genres)  # Artist-genre ilişkisini ekle
    
    # timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Fact table insert (without lyric)
    query = """
        INSERT INTO Transactions (timestamp, artist_id, track_name, release_date)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (current_timestamp, artist_id_db, track_name, formatted_release_date))

conn.commit()
cursor.close()
conn.close()

print("Database updated successfully with Spotify data.")
