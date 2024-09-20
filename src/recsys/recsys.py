from fastapi import FastAPI
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict
import os
import pandas as pd
import sqlite3
import pickle
import sklearn
import numpy as np


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
    


@app.post("/connect_db")
async def connect_sqlite_db():
    try:
        conn = sqlite3.connect("songs.db")
        logger.info("Connected to SQLite database")
        return {"status": "connection succesful"}
    except sqlite3.Error as e:
        logger.info("Error connecting to SQLite database")


@app.post("/track_name_query")
async def get_track_name(transaction_id: int):
    """Track id based query for obtaining a specific track name"""
  
    try:
        conn = sqlite3.connect("songs.db")
        logger.info("Connected to SQLite database")

        ## Track_id based recommendation

        #select the track info
        query = """SELECT Tr.track_name
                FROM Transactions AS Tr
                WHERE Tr.transaction_id={};""".format(transaction_id)

        rows = execute_select_query(conn, query)

        logger.info(type(rows), len(rows))
        
        return {"track_name": rows[0]}

    except Exception as e:
        logger.info(f"Error in recommendation script: {e}")

  


@app.post("/get_recommendation")
async def get_recommendation(track_name: str):

    folder_name = "ML_models/"
    model_name = 'RecSys_track_name.pkl'

    try:
        with open(folder_name+model_name, 'rb') as file:
            model_dict = pickle.load(file)

        df = model_dict["dataframe"]
        vectorizer = model_dict["vectorizer"]
        count_matrix = model_dict["count_matrix"]

        recs = get_recommendation_title(track_name, vectorizer, count_matrix, df)

        return {"Recommendations": recs}

    except Exception as e:
        logger.info(f"Error in recommendation script: {e}")

  

def get_recommendation_title(track_name, vectorizer, count_matrix, df):
    input_df = pd.DataFrame(columns=["track_name"])
    input_df.at[0, "track_name"] = track_name
    feature_vector = vectorizer.transform(input_df["track_name"])
    result = feature_vector.dot(count_matrix.T).toarray().reshape(-1)
    logger.info(result.shape)
    try: 
        ind1 = np.argsort(result,axis=0)[::-1][:10]
    except Exception as e:
        logger.info(e)

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