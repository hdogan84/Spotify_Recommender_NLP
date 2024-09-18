import sqlite3

# sqlite db
db_filename = 'songs.db'

# connect
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Drop existing tables
cursor.execute("DROP TABLE IF EXISTS Lyrics")
cursor.execute("DROP TABLE IF EXISTS Artists")
cursor.execute("DROP TABLE IF EXISTS Transactions")
cursor.execute("DROP TABLE IF EXISTS Genres")
cursor.execute("DROP TABLE IF EXISTS Tracks")

# Commit and close connection
conn.commit()
conn.close()

print("Existing tables dropped successfully.")
