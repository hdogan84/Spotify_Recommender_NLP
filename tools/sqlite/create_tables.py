import sqlite3

# 5. SQLite connection
db_filename = 'songs.db'
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
        release_date DATE,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (lyric_id) REFERENCES Lyrics(lyric_id)
    )
""")
