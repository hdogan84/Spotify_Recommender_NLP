import os
import mysql.connector

# read .env
db_config = {
    'user': 'root', 
    'password': os.getenv('MYSQL_ROOT_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE')
}


conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS Artists (
        artist_id INT AUTO_INCREMENT PRIMARY KEY,
        artist_name VARCHAR(255) NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Genres (
        genre_id INT AUTO_INCREMENT PRIMARY KEY,
        genre_desc VARCHAR(255) NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Lyrics (
        lyric_id INT AUTO_INCREMENT PRIMARY KEY,
        lyric TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Artist_Genres (
        artist_id INT,
        genre_id INT,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),
        PRIMARY KEY (artist_id, genre_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME NOT NULL,
        artist_id INT,
        track_name VARCHAR(255),
        lyric_id INT,
        release_date DATE,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (lyric_id) REFERENCES Lyrics(lyric_id)
    )
""")


conn.commit()
cursor.close()
conn.close()

print("Tables created successfully in 'music_db'.")
