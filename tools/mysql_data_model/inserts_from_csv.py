import mysql.connector
import pandas as pd
from datetime import datetime

db_config = {
    'user': 'root',                  
    'password': 'my-secret-pw',      
    'host': 'mysql',                 
    'database': 'music_db'           
}

csv_path = "/app/data/tcc_ceds_music.csv"

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# read CSV file
data = pd.read_csv(csv_path)
columns = ["artist_name", "track_name", "release_date", "genre", "lyrics", "len"]
data = data[columns]

# Format 'release_date' to 'YYYY-MM-DD'
data['release_date'] = pd.to_datetime(data['release_date'], format='%Y', errors='coerce').dt.strftime('%Y-%m-%d')

def insert_or_get_id(table, id_column, value_column, value):
    cursor.execute(f"SELECT {id_column} FROM {table} WHERE {value_column} = %s", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(f"INSERT INTO {table} ({value_column}) VALUES (%s)", (value,))
    return cursor.lastrowid

for _, row in data.iterrows():
    artist_name = row['artist_name'].lower()
    track_name = row['track_name'].lower()
    genre = row['genre'].lower()
    lyrics = row['lyrics'].lower()

    artist_id = insert_or_get_id("Artists", "artist_id", "artist_name", artist_name)
    genre_id = insert_or_get_id("Genres", "genre_id", "genre_desc", genre)

    # insert artist_genres
    cursor.execute("""
        INSERT IGNORE INTO Artist_Genres (artist_id, genre_id)
        VALUES (%s, %s)
    """, (artist_id, genre_id))

    lyrics_id = insert_or_get_id("Lyrics", "lyric_id", "lyric", lyrics)

    # timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # insert transactions
    cursor.execute("""
        INSERT INTO Transactions (timestamp, artist_id, track_name, release_date, lyric_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (current_timestamp, artist_id, track_name, row['release_date'], lyrics_id))

conn.commit()
cursor.close()
conn.close()

print("Database 'music_db' updated successfully with data from CSV file.")
