import sqlite3
import pandas as pd

# Define the database filename
db_filename = 'songs.db'

csv_path = "../../data/music-dataset-1950-to-2019/tcc_ceds_music.csv"

# Connect to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

 # Create a new table called 'tracks'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        artist VARCHAR(255) NOT NULL,
        track_name VARCHAR(255) NOT NULL,
        release_year INT, 
        genre VARCHAR(100),
        lyrics VARCHAR(10000), 
        len VARCHAR(10)
    )
""")
print("Table 'tracks' created or already exists.")

# Read the CSV file
data = pd.read_csv(csv_path)
columns = ["artist_name","track_name","release_date","genre", "lyrics","len"]
data = data[columns]


# Insert data into the 'tracks' table
for _, row in data.iterrows():
    cursor.execute("""
        INSERT INTO tracks (artist, track_name, release_year, genre, lyrics, len)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tuple(row))


# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database '{db_filename}' created successfully with data from csv file.")
