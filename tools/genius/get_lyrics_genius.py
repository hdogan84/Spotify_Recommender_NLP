from bs4 import BeautifulSoup as bs
import requests 
import pandas as pd
import random
from urllib.parse import urljoin
import time
from datetime import datetime
from dotenv import load_dotenv
import os

"""This script acquires lyrics information for the data frame with 500k spotify tracks
Each time it is called, acquires more lyrics and saves the latest versions of both the main csv file 
and the partition that contain lyrics. 
In this way, the script is suitable for scheduling and it will update the existing data each time it is called. 
Initially, the lyrics field is initialized as " " and ~1000 lyrics have been acquired."""


def get_song_info(song_title, artist_name, ACCESS_TOKEN):
    # Genius API arama URL'si
    search_url = 'https://api.genius.com/search'
    
    # Arama için gerekli parametreler
    params = {
        'q': f'{song_title} {artist_name}'
    }  
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    
    # Şarkıyı Genius API'de arama
    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()

    if response.status_code != 200:
        print(f"Warning: Request not successful. Status: {response.status_code}")
    
    if len(data['response']['hits']) == 0:
        return 0       
        
    song_info = data['response']['hits'][0]['result']
    
    return song_info

def get_lyrics(song_url, song_name, artist):
    page = requests.get(song_url)
    soup = bs(page.content,"lxml")
    
    tags = soup.find_all('div', attrs={'class': "Lyrics__Container-sc-1ynbvzw-1 kUgSbL"})

    if len(tags)<1:
        print(f"No lyrics found at ULR: {song_url}")
        return " "

    try: 
        lyrics = " "
        for tag in tags:
            lyrics += tag.get_text(separator="\n")

        print(f"Found lyrics for: {song_name}")

    except Exception as err:
        #print(err)
        print(f"Could not find lyrics. Title: {song_name}, Artist: {artist}")
        lyrics = " " #Assign a string with an empty spaces. The final return will be one empty space, as the first initialization

    finally:
        return lyrics


def get_genius_lyrics(song_title, artist_name, access_token):

    song_info = get_song_info(song_title, artist_name, access_token)

    if song_info == 0:
        print(f"Genius API search NULL for: {song_title} - {artist_name}")
        return " "

    song_url = song_info['url']
    lyrics = get_lyrics(song_url, song_title, artist_name)
    
    return lyrics


if __name__ == "__main__":

    load_dotenv()
    ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')
    response_wait_time = 2 #Between two API requests

    df_tracks = pd.read_csv("../../data/spotify_tracks_with_lyrics.csv")

    # Find out which tracks have lyrics field as NULL. 
    indx = df_tracks[df_tracks.lyrics==" "].index.tolist()

    # Sample a specific amount of data, to perform query for. 
    num_samples = 10
    row_indx = random.sample(indx, num_samples)
    
    for i in row_indx:
        song_title = df_tracks.at[i, "Song_title"]
        artist_name = df_tracks.at[i, "Artist"]
        
        lyrics = get_genius_lyrics(song_title, artist_name, ACCESS_TOKEN)
        df_tracks.at[i, "lyrics"] = lyrics
        time.sleep(response_wait_time)


    # Get the dataframe with lyrics info
    df_lyrics = df_tracks[df_tracks["lyrics"]!=" "]

    # Save the updated version of main data to local folder
    df_tracks.to_csv("../../data/spotify_tracks_with_lyrics.csv", index=False)

    # Save the latest version of the data with acquired lyrics
    # Datetime in file not needed. One can get "last modified" date of file, if necessary
    df_lyrics.to_csv(f"../../data/spotify_genius_lyrics.csv", index=False)

    print(len(df_lyrics))
