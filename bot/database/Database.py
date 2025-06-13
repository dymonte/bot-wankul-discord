import pymongo 
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))

class Database:
    def __init__(self):
        """
        Initialize a connection to the MongoDB database.

        The connection is established with the host and port found in the
        environment variables DB_HOST and DB_PORT. The database used is named
        "botWankul".
        """
        
        self.client = pymongo.MongoClient(DB_HOST, DB_PORT)
        
        self.db=self.client["botWankul"]
