import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import json
from datetime import datetime

# Test data
mock_playlist_response = {
    'items': [
        {
            'track': {
                'name': 'Test Track',
                'artists': [{'name': 'Test Artist', 'id': 'test_artist_id'}],
                'album': {'release_date': '2020'}
            }
        }
    ]
}

mock_genre_response = {
    'artists': [
        {
            'id': 'test_artist_id',
            'genres': ['Test Genre', 'Alternative']
        }
    ]
}

# Mock insert_or_get_id
def mock_insert_or_get_id(table, id_column, value_column, value):
    if table == "Artists":
        return 1  # Mock artist_id
    elif table == "Genres":
        return 2  # Mock genre_id
    elif table == "Transactions":
        return 3  # Mock transaction_id

@pytest.fixture
def mock_db():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

# Helper function to get genres for an artist
def get_genres_for_artist(artist_id):
    for artist in mock_genre_response['artists']:
        if artist['id'] == artist_id:
            return artist['genres']  # Return genres for the artist
    return []

@patch('mysql.connector.connect')
@patch('requests.post')
@patch('requests.get')
def test_spotify_top_50(mock_get, mock_post, mock_connect, mock_db):
    mock_conn, mock_cursor = mock_db
    mock_connect.return_value = mock_conn

    # Mock API
    mock_post.return_value.json.return_value = {'access_token': 'mock_token'}
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: mock_playlist_response),  # Playlist response
        MagicMock(status_code=200, json=lambda: mock_genre_response)      # Genre response
    ]

    # insert into tables
    from spotifytop50 import insert_or_get_id

    # Mock insert_or_get_id
    with patch('spotifytop50.insert_or_get_id', side_effect=mock_insert_or_get_id):
        
        # read data
        for item in mock_playlist_response['items']:
            json_track_name = item['track']['name']
            json_release_date = item['track']['album']['release_date']
            json_release_date = pd.to_datetime(json_release_date, format='%Y', errors='coerce').strftime('%Y-%m-%d')

            # artists
            for artist in item['track']['artists']:
                json_artist_name = artist['name']
                artist_id = artist['id']

                # Get genres for this artist
                artist_genres = get_genres_for_artist(artist_id)
                
                # Process each genre for the artist
                for genre in artist_genres:
                    artist_id = mock_insert_or_get_id("Artists", "artist_id", "artist_name", json_artist_name)
                    genre_id = mock_insert_or_get_id("Genres", "genre_id", "genre_desc", genre)
                    transaction_id = mock_insert_or_get_id("Transactions", "transaction_id", "track_name", json_track_name)

                    # insert simulations
                    mock_cursor.execute(f"INSERT INTO Artists (artist_id, artist_name) VALUES (%s, %s)",
                                        (artist_id, json_artist_name))
                   
                    mock_cursor.execute(f"INSERT INTO Genres (genre_id, genre_desc) VALUES (%s, %s)",
                                        (genre_id, genre))

                    mock_cursor.execute(f"INSERT INTO Artist_genres (artist_id, genre_id) VALUES (%s, %s)",
                                        (artist_id, genre_id))

                    # timestamp
                    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    mock_cursor.execute(f"INSERT INTO Transactions (transaction_id, timestamp, track_name, artist_id, release_date) VALUES (%s, %s, %s, %s, %s)",
                                        (transaction_id, current_timestamp, json_track_name, artist_id, json_release_date))

                    # Asserts
                    mock_cursor.execute.assert_any_call(
                        "INSERT INTO Artists (artist_id, artist_name) VALUES (%s, %s)",
                        (artist_id, json_artist_name)
                    )
                    
                    mock_cursor.execute.assert_any_call(
                        "INSERT INTO Genres (genre_id, genre_desc) VALUES (%s, %s)",
                        (genre_id, genre)
                    )

                    mock_cursor.execute.assert_any_call(
                        "INSERT INTO Artist_genres (artist_id, genre_id) VALUES (%s, %s)",
                        (artist_id, genre_id)
                    )

                    mock_cursor.execute.assert_any_call(
                        "INSERT INTO Transactions (transaction_id, timestamp, track_name, artist_id, release_date) VALUES (%s, %s, %s, %s, %s)",
                        (transaction_id, current_timestamp, json_track_name, artist_id, json_release_date)
                    )

        # call commit 1 time
        mock_conn.commit.assert_called_once()
