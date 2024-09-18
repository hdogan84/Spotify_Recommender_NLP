import requests
import base64
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime  # Günün tarihini almak için ekledik

load_dotenv()

# 1. Client ID - Client Secret
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# 2. OAuth Token alımı
auth_url = 'https://accounts.spotify.com/api/token'
auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode('utf-8')

response = requests.post(auth_url, headers={
    'Authorization': f'Basic {auth_header}',
    'Content-Type': 'application/x-www-form-urlencoded'
}, data={'grant_type': 'client_credentials'})

token = response.json().get('access_token')

# 3. Top 50 Global playlist
playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Top 50 Global playlist ID
playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

playlist_response = requests.get(playlist_url, headers={
    'Authorization': f'Bearer {token}'
})

tracks = playlist_response.json()['items']

# 4. Artist bilgisi ile genre bilgisi çekme fonksiyonu
def get_artist_genres(artist_id):
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    artist_response = requests.get(artist_url, headers={
        'Authorization': f'Bearer {token}'
    })
    artist_data = artist_response.json()
    return artist_data.get('genres', ['Unknown'])

# 5. SQLite bağlantısı ve tablo oluşturma
db_filename = 'songs.db'
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Yeni tablo oluşturma işlemleri
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Artists (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_name TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Genres (
        genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
        genre_desc TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Artist_Genres (
        artist_id INTEGER,
        genre_id INTEGER,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),
        PRIMARY KEY (artist_id, genre_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Lyrics (
        lyric_id INTEGER PRIMARY KEY AUTOINCREMENT,
        lyric TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        artist_id INTEGER,
        track_name VARCHAR(255),
        lyric_id INTEGER,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (lyric_id) REFERENCES Lyrics(lyric_id)
    )
""")

print("Tables created or already exist.")

# 6. Spotify verilerini işleme ve SQLite'a ekleme
def insert_or_get_id(table, id_column, value_column, value):
    cursor.execute(f"SELECT {id_column} FROM {table} WHERE {value_column} = ?", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(f"INSERT INTO {table} ({value_column}) VALUES (?)", (value,))
    return cursor.lastrowid

def insert_artist_genres(artist_id_db, genres):
    for genre in genres:
        genre = genre.lower()
        genre_id = insert_or_get_id("Genres", "genre_id", "genre_desc", genre)
        cursor.execute("""
            INSERT OR IGNORE INTO Artist_Genres (artist_id, genre_id)
            VALUES (?, ?)
        """, (artist_id_db, genre_id))

for track in tracks:
    track_name = track['track']['name'].strip().lower()
    artist_name = track['track']['artists'][0]['name'].strip().lower()
    artist_id = track['track']['artists'][0]['id']
    
    # artist-genres information
    genres = get_artist_genres(artist_id)
    
    # inserts
    artist_id_db = insert_or_get_id("Artists", "artist_id", "artist_name", artist_name)
    insert_artist_genres(artist_id_db, genres)  # Artist-genre ilişkisini ekle
    
    # timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Fact table insert (without lyric)
    cursor.execute("""
        INSERT INTO Transactions (timestamp, artist_id, track_name)
        VALUES (?, ?, ?)
    """, (current_timestamp, artist_id_db, track_name))

conn.commit()
conn.close()

print(f"Database '{db_filename}' updated successfully with Spotify data.")
