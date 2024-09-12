import numpy as np
import pandas as pd
import pickle

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics.pairwise import cosine_similarity

folder_name = "../../data/ML_models/"
model_name = 'RecSys_track_name.pkl'


with open(folder_name+model_name, 'rb') as file:
    model_dict = pickle.load(file)

 
# Use one split from Spotify (other than fold 0) as test data
df_spotify = pd.read_csv("../../data/spotify_track_ids.csv")
df_spotify = df_spotify.drop("Unnamed: 0", axis=1)
df_spotify = df_spotify.rename(columns={"Song_title": "track_name", "Artist": "artist_name"})
df_spotify.track_name = df_spotify.track_name.astype(str)
df_spotify.track_name = df_spotify.track_name.apply(lambda x: x.lower())
df_spotify.artist_name = df_spotify.artist_name.astype(str)
df_spotify.artist_name = df_spotify.artist_name.apply(lambda x: x.lower())


skf = StratifiedKFold(n_splits=5, random_state=421, shuffle=True)

for i, (train_ind, test_ind) in enumerate(skf.split(df_spotify.track_name, df_spotify.artist_name)):
    df_spotify.loc[test_ind,"fold"] = i

df_spotify.fold = df_spotify.fold.astype(int)

 
# Choose a Spotify split as test data
fold_number = 2

df_test = df_spotify[df_spotify.fold == 2]
df_test = df_test[["track_name", "artist_name"]].reset_index(drop=True)
df_test = df_test.drop_duplicates()
df_test = df_test.reset_index(drop=True)


 
# Load model variables from pickle
df = model_dict["dataframe"]
vectorizer = model_dict["vectorizer"]
count_matrix = model_dict["count_matrix"]
count_matrix.shape

 

def get_recommendation_title(ind) :
    feature_vector = vectorizer.transform(pd.DataFrame(df_test["track_name"]).iloc[ind])
    result = np.dot(feature_vector, count_matrix.T).toarray()[0]
    ind1 = np.argsort(result)[::-1][:10]
    return df.loc[ind1]



if __name__ == "__main__":
    
    ind = 900
    song=df_test.loc[ind]["track_name"]
    singer=df_test.loc[ind]["artist_name"]
    print("The input singer and song name is: ")
    print(singer, "  ", song)

    recs = get_recommendation_title(ind)
    print("\nRecommendations:")
    print(recs)
    	




