import numpy as np
import pandas as pd
import pickle
import sys

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics.pairwise import cosine_similarity

df_kaggle = pd.read_csv("../../data/music-dataset-1950-to-2019/tcc_ceds_music.csv")
columns = ["artist_name", "track_name"]
df_kaggle = df_kaggle[columns]
print(df_kaggle.track_name.isna().sum())

df_spotify_0 = pd.read_csv("../../data/ML_models/train_data/spotify_tracks_500k_fold0.csv")
df_spotify_0 = df_spotify_0[["track_name", "artist_name"]].reset_index(drop=True)
df_spotify_0 = df_spotify_0.dropna()
print(df_spotify_0.artist_name.isna().sum())

df = pd.concat([df_kaggle, df_spotify_0],axis=0)
df = df[["artist_name", "track_name"]]
df = df.drop_duplicates()
df = df.reset_index(drop=True)
print(len(df))

vectorizer = CountVectorizer(max_features=15000)
count_matrix = vectorizer.fit_transform(df.track_name)
count_matrix = count_matrix.astype(np.int16)

#cosine_sim = cosine_similarity(count_matrix, count_matrix, dense_output=False)

model_dict=dict()
model_dict["vectorizer"] = vectorizer
model_dict["dataframe"] = df
model_dict["count_matrix"] = count_matrix

folder = "../../data/ML_models/"
filename = 'RecSys_track_name.pkl'

with open(folder+filename, 'wb') as file:
    # Serialize the dictionary and save it to the file
    pickle.dump(model_dict, file)




    	




