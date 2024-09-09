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
        artist_name VARCHAR(255) NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Genres (
        genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
        genre_desc VARCHAR(255) NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tracks (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_name VARCHAR(255) NOT NULL
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
        timestamp DATE NOT NULL,
        track_id INTEGER,
        artist_id INTEGER,
        genre_id INTEGER,
        lyrics_id INTEGER,
        FOREIGN KEY (track_id) REFERENCES Tracks(track_id),
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),
        FOREIGN KEY (lyrics_id) REFERENCES Lyrics(lyric_id)
    )
""")


def get_table_names(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        return [table[0] for table in tables]
    except sqlite3.Error as e:
        print(f"Error fetching table names: {e}")
        return None

if conn is not None:
    # Get table names
    table_names = get_table_names(conn)
    
    if table_names:
        print("\nTables in the database:")
        for name in table_names:
            print(name)
    else:
        print("No tables found or an error occurred.")

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
    artist_id = insert_or_get_id("Artists", "artist_id", "artist_name", row['artist_name'])
    genre_id = insert_or_get_id("Genres", "genre_id", "genre_desc", row['genre'])
    track_id = insert_or_get_id("Tracks", "track_id", "track_name", row['track_name'])
    lyrics_id = insert_or_get_id("Lyrics", "lyric_id", "lyric", row['lyrics'])
    
    # Fact table insert
    cursor.execute("""
        INSERT INTO Transactions (timestamp, track_id, artist_id, genre_id, lyrics_id)
        VALUES (?, ?, ?, ?, ?)
    """, (row['release_date'], track_id, artist_id, genre_id, lyrics_id))


conn.commit()
conn.close()

print(f"Database '{db_filename}' updated successfully with data from CSV file.")