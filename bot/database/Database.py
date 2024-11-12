import pymongo 
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))

class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(DB_HOST, DB_PORT)
        
        self.db=self.client["botWankul"]
