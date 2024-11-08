from fastapi import FastAPI
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict
import os
#import pandas as pd
#import sqlite3
import subprocess

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

@app.get("/status")
async def get_status():
    return {"status": "InitDB API is up"}

@app.post("/create-tables")
def create_tables():
    result = subprocess.run(['python3', '/app/tools/mysql_data_model/create_tables.py'], capture_output=True, text=True)

    if result.returncode == 0:
        return {"message": "Tables created successfully.", "output": result.stdout}
    else:
        return {"error": result.stderr}, 500

@app.post("/insert-from-csv")
def insert_from_csv():
    # run /app/tools/mysql_data_model/inserts_from_csv.py
    result = subprocess.run(['python3', '/app/tools/mysql_data_model/inserts_from_csv.py'], capture_output=True, text=True)

    if result.returncode == 0:
        # Başarılı sonuç olursa, sonucu dönüyoruz
        return {"message": "CSV data inserted successfully.", "output": result.stdout}
    else:
        # return error
        return {"error": result.stderr}, 500

@app.post("/spotify-top-50")
def insert_spotify_top_50():
    # run /app/tools/mysql_data_model/spotifytop50.py
    result = subprocess.run(['python3', '/app/tools/mysql_data_model/spotifytop50.py'], capture_output=True, text=True)

    if result.returncode == 0:
        return {"message": "Spotify Top 50 data inserted successfully.", "output": result.stdout}
    else:
        return {"error": result.stderr}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)



  



