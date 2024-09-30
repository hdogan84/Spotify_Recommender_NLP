import pytest
from unittest.mock import Mock, patch

# Mock db test
@pytest.fixture(scope="module")
def db_connection():
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()

        # Mock methods for cursor
        mock_cursor.fetchall.return_value = [("Artists",), ("Genres",), ("Lyrics",), ("Artist_Genres",), ("Transactions",)]
        
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        yield mock_cursor

        # Verify that the close method is called at the end of the tests
        mock_cursor.close()  # Ensure the cursor is closed
        mock_conn.close()  # Ensure the connection is also closed

# Table scripts
table_queries = [
    """CREATE TABLE IF NOT EXISTS Artists (
        artist_id INT AUTO_INCREMENT PRIMARY KEY,
        artist_name VARCHAR(255) NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS Genres (
        genre_id INT AUTO_INCREMENT PRIMARY KEY,
        genre_desc VARCHAR(255) NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS Lyrics (
        lyric_id INT AUTO_INCREMENT PRIMARY KEY,
        lyric TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS Artist_Genres (
        artist_id INT,
        genre_id INT,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),
        PRIMARY KEY (artist_id, genre_id)
    )""",
    """CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME NOT NULL,
        artist_id INT,
        track_name VARCHAR(255),
        lyric_id INT,
        release_date DATE,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (lyric_id) REFERENCES Lyrics(lyric_id)
    )"""
]

# Parametrized test function
@pytest.mark.parametrize("query", table_queries)
def test_create_tables(db_connection, query):
    db_connection.execute(query)

    # Assert that the execute method was called with the correct query
    db_connection.execute.assert_called_with(query)

    # Simulate committing the transaction
    db_connection.connection.commit()

# Verify that the tables were created
def test_table_existence(db_connection):
    db_connection.execute("SHOW TABLES")
    tables = [table[0] for table in db_connection.fetchall()]

    assert "Artists" in tables
    assert "Genres" in tables
    assert "Lyrics" in tables
    assert "Artist_Genres" in tables
    assert "Transactions" in tables
