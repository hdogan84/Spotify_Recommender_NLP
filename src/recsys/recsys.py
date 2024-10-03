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
import mysql.connector
from mysql.connector import Error as mysqlError

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

db_config = {
    'user': 'root', 
    'password': os.getenv('MYSQL_ROOT_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE')
}


@app.post("/connect_mysql")
async def connect_mysql_db():
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            logger.info("Successfully connected to the database")

            # Create a cursor to perform database operations
            cursor = connection.cursor()

            # Execute a simple query
            cursor.execute("SELECT DATABASE();")

            # Fetch the result
            record = cursor.fetchone()
            logger.info(f"Connected to the database: {record}")

            # Fetch the result
            record = cursor.fetchall()
            logger.info(f"Number of records: {len(record)}")

            return {"Status": "Connected"}
            

    except mysqlError as e:
        logger.info(f"Error: {e}")

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection is closed")



@app.post("/track_name_query")
async def get_track_name(transaction_id: int):
    """Track id based query for obtaining a specific track name"""
  
    try:
        connection = mysql.connector.connect(
            host='mysql',  # or '127.0.0.1' if you're running the script locally
            port=3306,  # Default MySQL port
            user='root',
            password='my-secret-pw',  # The password set when running the container
            database='music_db'  # The MySQL database
        )
        logger.info("Connected to mysql database")


        #select the track info
        query = """SELECT Tr.track_name
                FROM Transactions AS Tr
                WHERE Tr.transaction_id={};""".format(transaction_id)

        cursor = connection.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

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