from fastapi import FastAPI
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict
import os
#import pandas as pd
import sqlite3

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

  



