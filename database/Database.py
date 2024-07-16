import pymongo 

class Database:
    
    def __init__(self):

        self.client = pymongo.MongoClient("localhost", 27017)
        
        self.db=self.client["botWankul"]



# exemple={"_id":"2322872", "users":[
#     {"id_user": 1, "last_roll":(0,0,0), "cards":{
#         "25":3 #id de la carte + la quantité
#     }},
#     {"id_user": 2, "last_roll":(0,0,0), "cards":{}},
# ]}




