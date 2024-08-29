from fastapi import FastAPI
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict
import os
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
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

logger = logging.getLogger("init_db") 

app = FastAPI()

class FetchModelRequest(BaseModel):
    db_name: str = "mysql"
    dataset: str = "music-dataset-1950-to-2019"
    

@app.get("/status")
async def get_status():
    return {"status": "InitDB API is up"}

@app.post("/fetch_data")
async def fetch_csv_data(request: FetchModelRequest):
    db_name = request.db_name
    dataset_name = request.dataset

    try:
        logger.info("Entered the try structure in init_db.py")
        data_path = "../data/"
        download_datasets(data_path)
        logger.info(f"Datasets downloaded to {data_path}")

        dataset_path = data_path + dataset_name
        cached_datasets = prepare_datasets(dataset_path, dataset_name)
        logger.info(f"Datasets prepared from {dataset_path}")

        songs = cached_datasets[dataset_name]
        
        logger.info("Data load as DF successful")
        logger.info("----------------------------------------------------------")
        return {"status": "Dataload succesful"}

    except Exception as e:
        logger.error(f"Error during data loading: {e}")
        return {"error": "Dataload failed"}

    ## Try DB connect and data dump here

@app.post("/connect_db")
async def connect_mysql_db():
    try:
        # Establish a connection to the MySQL database
        logger.info("Entered try block in connect end")
        connection = mysql.connector.connect(
            host='mysql-svc',  # or '127.0.0.1' if you're running the script locally
            port=3306,  # Default MySQL port
            user='root',
            password='my-secret-pw',  # The password you set when running the container
            #database='songs'  # The default MySQL database, or you can specify another one
        )

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
            logger.info(f"Connected to the database: {len(record)}")

    except mysqlError as e:
        logger.info(f"Error: {e}")

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection is closed")


def download_datasets(download_path, dataset_owner="saurabhshahane", dataset_name="music-dataset-1950-to-2019"):
    logger.info("Entered the download_datasets function.")
    api = KaggleApi()
    api.authenticate()

    dataset_folder = os.path.join(download_path, dataset_name)
    logger.info(f"dataset_folder from download_datasets(): {dataset_folder}")
    if not os.path.exists(dataset_folder):
        os.mkdir(dataset_folder)
        logger.info("Data folder created.")
    #convert this operation to try except
    api.dataset_download_files(dataset_owner + "/" + dataset_name, path=dataset_folder, unzip=True)
    logger.info("Datasets are downloaded and unzipped.")

global dataset_cache
dataset_cache = {}

def prepare_datasets(path_to_dataset, dataset_name):
    global dataset_cache
    if dataset_name in dataset_cache:
        logger.info("Using cached datasets")
        return dataset_cache

    songs_1950_2019 = load_datasets_in_workingspace(path_to_datasets=path_to_dataset)
    
    logger.info("All test and train sets successfully prepared.")

    dataset_cache[dataset_name] = songs_1950_2019

    return dataset_cache

def load_datasets_in_workingspace(path_to_datasets="./music-dataset-1950-to-2019"):
    songs_1950_2019 = pd.read_csv(path_to_datasets + "/" + "tcc_ceds_music.csv")
    return songs_1950_2019