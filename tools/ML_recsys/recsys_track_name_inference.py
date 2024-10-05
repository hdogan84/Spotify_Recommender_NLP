import numpy as np
import pandas as pd
import pickle
import sys

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics.pairwise import cosine_similarity


def get_recommendation_title(track_name) :

    if track_name == "" or track_name==None or type(track_name)!=str:
        raise Exception("Input track name must be a valid string variable")

    folder_name = "../../data/ML_models/"
    model_name = 'RecSys_track_name.pkl'

    with open(folder_name+model_name, 'rb') as file:
        model_dict = pickle.load(file)

    # Load model variables from pickle
    df = model_dict["dataframe"]
    vectorizer = model_dict["vectorizer"]
    count_matrix = model_dict["count_matrix"]
    count_matrix.shape

    single_df = pd.DataFrame([track_name], columns=["track_name"])
    feature_vector = vectorizer.transform(single_df.iloc[0])
    result = np.dot(feature_vector, count_matrix.T).toarray()[0]
    ind1 = np.argsort(result)[::-1][:10]
    
    return df.loc[ind1]


if __name__ == "__main__":
    
    # Use one split from Spotify (other than fold 0) as test data
    fold_number = int(sys.argv[1])

    # use a random index to choose a track name
    ind = int(sys.argv[2])

    # load the test data 
    df_test = pd.read_csv(f"../../data/ML_models/test_data/spotify_tracks_500k_fold{fold_number}.csv")

    song=df_test.loc[ind]["track_name"]
    singer=df_test.loc[ind]["artist_name"]
    print("The input singer and song name is: ")
    print(singer, "  ", song)

    recs = get_recommendation_title(song)
    print("\nRecommendations:")
    print(recs)
    	




