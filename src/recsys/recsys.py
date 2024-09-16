from fastapi import FastAPI
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict
import os
import pandas as pd
import sqlite3
import pickle
import sklearn


# Define the path for the log file. This code is the same in each container, the log file is a bind mount defined in the docker-compose.yaml --> All containers write in this bind mount log file.
log_file_path = Path("reports/logs/app.log")

# Configure the logging to write to the specified file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, mode='a'),  # 'a' for append, 'w' for overwrite
        logging.StreamHandler()  # This will also print to console
    ]
)

logger = logging.getLogger("recsys") 

app = FastAPI()

class FetchModelRequest(BaseModel):
    db_name: str = "songs.db"
    
    

@app.get("/status")
async def get_status():
    return {"status": "InitDB API is up"}


@app.post("/connect_db")
async def connect_sqlite_db():
    try:
        conn = sqlite3.connect("songs.db")
        logger.info("Connected to SQLite database")
        return {"status": "connection succesful"}
    except sqlite3.Error as e:
        logger.info("Error connecting to SQLite database")


@app.post("/get_recommendation")
async def get_recommendation():

    #return {"res": os.listdir("./ML_models")}

    folder_name = "ML_models/"
    model_name = 'RecSys_track_name.pkl'

    try:
        with open(folder_name+model_name, 'rb') as file:
            model_dict = pickle.load(file)

        df = model_dict["dataframe"]
        vectorizer = model_dict["vectorizer"]
        count_matrix = model_dict["count_matrix"]

        conn = sqlite3.connect("songs.db")
        logger.info("Connected to SQLite database")


        ## Track_id based recommendation
        ## needs to be imroved further for specific query
        track_id_input = 9

        #select the track info
        query = """SELECT A.artist_name, COUNT(*) as track_count
                FROM Transactions AS T
                JOIN Artists AS A ON T.artist_id = A.artist_id
                GROUP BY A.artist_name
                ORDER BY track_count DESC
                LIMIT 10;"""     

        #select artists and their tracks
        query = """SELECT A.artist_name, T.track_name
                    FROM Transactions AS Tr
                    WHERE Tr.transaction_id=3
                    JOIN Artists AS A ON Tr.artist_id = A.artist_id
                    JOIN Tracks AS T ON Tr.track_id = T.track_id;""" 

        rows = execute_select_query(conn, query)

        logger.info(type(rows), len(rows))
        
        return {"res": rows}

        ## will proceed with this part once the query works properly
        song=rows[0][0]
        singer=rows[0][1]
        print("The input singer and song name is: ")
        print(singer, "  ", song)

        recs = get_recommendation_title(ind)

        return {"Result": "connection succesful"}

    except sqlite3.Error as e:
        logger.info("Error in recommendation script")

  

def get_recommendation_title(ind) :
    feature_vector = vectorizer.transform(pd.DataFrame(df_test["track_name"]).iloc[ind])
    result = np.dot(feature_vector, count_matrix.T).toarray()[0]
    ind1 = np.argsort(result)[::-1][:10]
    return df.loc[ind1]

def execute_select_query(conn, query):
    try:
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None