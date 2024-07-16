import pymongo 

class Database:
    
    def __init__(self):

        self.client = pymongo.MongoClient("localhost", 27017)
        
        self.db=self.client["botWankul"]




    def update_roll(self, id_guild, id_user, card_list, last_roll):

        self.players_table.update_one({"_id":id_guild, "users":{"$elemMatch":{"id_user":id_user}}},{"$set":{"users.$.last_roll":last_roll}})
        pass


# exemple={"_id":"2322872", "users":[
#     {"id_user": 1, "last_roll":(0,0,0), "cards":{
#         "25":3 #id de la carte + la quantité
#     }},
#     {"id_user": 2, "last_roll":(0,0,0), "cards":{}},
# ]}




