import sqlite3
import pandas as pd
from datetime import datetime

# sqlite db
db_filename = 'songs.db'

csv_path = "../../data/music-dataset-1950-to-2019/tcc_ceds_music.csv"

# connect
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# read from csv
data = pd.read_csv(csv_path)
columns = ["artist_name", "track_name", "release_date", "genre", "lyrics", "len"]
data = data[columns]

# dimension table insert
def insert_or_get_id(table, id_column, value_column, value):
    cursor.execute(f"SELECT {id_column} FROM {table} WHERE {value_column} = ?", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(f"INSERT INTO {table} ({value_column}) VALUES (?)", (value,))
    return cursor.lastrowid

for _, row in data.iterrows():
    # Convert to lowercase
    artist_name = row['artist_name'].lower()
    track_name = row['track_name'].lower()
    genre = row['genre'].lower()
    lyrics = row['lyrics'].lower()

    # Insert or get artist_id and genre_id
    artist_id = insert_or_get_id("Artists", "artist_id", "artist_name", artist_name)
    genre_id = insert_or_get_id("Genres", "genre_id", "genre_desc", genre)

    # Insert into Artist_Genres if not already exists
    cursor.execute("""
        INSERT OR IGNORE INTO Artist_Genres (artist_id, genre_id)
        VALUES (?, ?)
    """, (artist_id, genre_id))

    # Insert or get lyric_id
    lyrics_id = insert_or_get_id("Lyrics", "lyric_id", "lyric", lyrics)
    
     # timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   
    # Insert into Transactions we can insert current_timestamp like spotify code
    cursor.execute("""
        INSERT INTO Transactions (timestamp, artist_id, track_name, release_date, lyric_id)
        VALUES (?, ?, ?, ?, ?)
    """, (current_timestamp, artist_id, track_name, row['release_date'], lyrics_id))

# Commit and close connection
conn.commit()
conn.close()

print(f"Database '{db_filename}' updated successfully with data from CSV file.")
