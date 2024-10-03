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



# exemple={"_id":"2322872", "users":[
#     {"id_user": 1, "last_roll":(0,0,0), "cards":{
#         "25":3 #id de la carte + la quantité
#     }},
#     {"id_user": 2, "last_roll":(0,0,0), "cards":{}},
# ]}




