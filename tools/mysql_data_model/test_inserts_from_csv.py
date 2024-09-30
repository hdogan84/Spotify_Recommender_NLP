import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# Test data
test_data = pd.DataFrame({
    "artist_name": ["Test Artist"],
    "track_name": ["Test Track"],
    "release_date": ["2020"],
    "genre": ["Test Genre"],
    "lyrics": ["Test Lyrics"],
    "len": [300]
})

# Mock insert_or_get_id
def mock_insert_or_get_id(table, id_column, value_column, value):
    if table == "Artists":
        return 1  # Mock artist_id
    elif table == "Genres":
        return 2  # Mock genre_id
    elif table == "Lyrics":
        return 3  # Mock lyric_id
    elif table == "Artist_genres":
        return 4  # Mock artist_genre_id
    elif table == "Transactions":
        return 5  # Mock transaction_id

@pytest.fixture
def mock_db():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

@patch('mysql.connector.connect')
@patch('pandas.read_csv')
def test_main_flow(mock_read_csv, mock_connect, mock_db):
    mock_conn, mock_cursor = mock_db
    mock_connect.return_value = mock_conn
    mock_read_csv.return_value = test_data

    # Mock insert_or_get_id
    with patch('inserts_from_csv.insert_or_get_id', side_effect=mock_insert_or_get_id):
        for index, row in test_data.iterrows():
            csv_artist_name = row['artist_name']
            csv_track_name = row['track_name']
            csv_release_date = pd.to_datetime(row['release_date'], format='%Y', errors='coerce').strftime('%Y-%m-%d')
            csv_genre = row['genre']
            csv_lyrics = row['lyrics']

            # get ids
            artist_id = mock_insert_or_get_id("Artists", "artist_id", "artist_name", csv_artist_name)
            genre_id = mock_insert_or_get_id("Genres", "genre_id", "genre_desc", csv_genre)
            lyric_id = mock_insert_or_get_id("Lyrics", "lyric_id", "lyric", csv_lyrics)
            transaction_id = mock_insert_or_get_id("Transactions", "transaction_id", "track_name", csv_track_name)

            # insert simulations
            mock_cursor.execute(f"INSERT INTO Artists (artist_id, artist_name) VALUES (%s, %s)",
                                (artist_id, csv_artist_name))
            mock_cursor.execute(f"INSERT INTO Genres (genre_id, genre_desc) VALUES (%s, %s)",
                                (genre_id, csv_genre))
            mock_cursor.execute(f"INSERT INTO Lyrics (lyric_id, lyric) VALUES (%s, %s)",
                                (lyric_id, csv_lyrics))

            mock_cursor.execute(f"INSERT INTO Artist_genres (artist_id, genre_id) VALUES (%s, %s)",
                                (artist_id, genre_id))
            
            # timestamp
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mock_cursor.execute(f"INSERT INTO Transactions (transaction_id, timestamp, track_name, artist_id, release_date) VALUES (%s, %s, %s, %s, %s)",
                                (transaction_id, current_timestamp, csv_track_name, artist_id, csv_release_date))

        # assert inserts
        mock_cursor.execute.assert_any_call(
            "INSERT INTO Artists (artist_id, artist_name) VALUES (%s, %s)",
            (artist_id, csv_artist_name)
        )

        mock_cursor.execute.assert_any_call(
            "INSERT INTO Genres (genre_id, genre_desc) VALUES (%s, %s)",
            (genre_id, csv_genre)
        )

        mock_cursor.execute.assert_any_call(
            "INSERT INTO Lyrics (lyric_id, lyric) VALUES (%s, %s)",
            (lyric_id, csv_lyrics)
        )

        mock_cursor.execute.assert_any_call(
            "INSERT INTO Artist_genres (artist_id, genre_id) VALUES (%s, %s)",
            (artist_id, genre_id)
        )

        mock_cursor.execute.assert_any_call(
            "INSERT INTO Transactions (transaction_id, timestamp, track_name, artist_id, release_date) VALUES (%s, %s, %s, %s, %s)",
            (transaction_id, current_timestamp, csv_track_name, artist_id, csv_release_date)
        )

    # db commit control
    mock_conn.commit.assert_called_once()