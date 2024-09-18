import sqlite3
import pandas as pd

# sqlite db
db_filename = 'songs.db'

csv_path = "../../data/music-dataset-1950-to-2019/tcc_ceds_music.csv"

# connect
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# table creations
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
    CREATE TABLE IF NOT EXISTS Lyrics (
        lyric_id INTEGER PRIMARY KEY AUTOINCREMENT,
        lyric TEXT
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
        INSERT INTO Transactions (timestamp, artist_id, track_name, lyric_id)
        VALUES (?, ?, ?, ?)
    """, (row['release_date'], artist_id, track_name, lyrics_id))

# Commit and close connection
conn.commit()
conn.close()

print(f"Database '{db_filename}' updated successfully with data from CSV file.")
