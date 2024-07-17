import discord, fbot
from database.Database import Database
from data.Cards import Cards



class PlayerDatabase(Database):

    def __init__(self) -> None:
        super().__init__()
        self.players_table=self.db["players"]


    def drop_table(self) -> None:
        """
        Supprime la table players
        TODO : Supprimer uniquement pour le serveur en question
        """
        self.players_table.drop()


    def get_player_data(self, id_guild : int, id_user : int)->dict:
        """
        Renvoie les informations du joueur sour forme d'un dictionnaire, 
        * si l'entrée dans la base de données n'existe pas, elle l'initialise avec des valeurs par défaut
        """
        guild_data=self.players_table.find_one({"_id":str(id_guild)})
        
        if guild_data==None:
            guild_data={"_id":str(id_guild), "players":{}}
            self.players_table.insert_one(guild_data)

        player_data=guild_data.get("players",{}).get(str(id_user),{})
        if player_data=={}:
            self.players_table.update_one({"_id":str(id_guild)},{"$set":{"players."+str(id_user):{"last_roll":(0,0,0), "money":0, "level":10, "color":"#ffffff", "number_of_rolls":0, "cards":{}}}})
            return {"last_roll":(0,0,0), "level":10, "number_of_rolls":0, "cards":{}}
        return player_data
    

    def can_roll(self, id_guild : int, id_user : int) -> bool:
        """
        Renvoie si le joueur peut roll
        """

        data=self.get_player_data(id_guild, id_user)
        if fbot.formated_date()==data.get("last_roll",(0,0,0)):
            return data.get("number_of_rolls",0)<data.get("level",1) 
        return True


    def update_roll(self, id_guild : int, id_user : int) -> int:
        """
        Met a jour la base de donnée pour le roll et renvoie le nombre de rolls restants

        """

        data=self.get_player_data(id_guild ,id_user)


        if fbot.formated_date()!=data.get("last_roll",(0,0,0)): # si l'heure a changée depuis le dernier roll
            print(f"heure changée pour {id_user}")
            self.players_table.update_one({"_id":str(id_guild)},{"$set":{"players."+str(id_user)+".last_roll":fbot.formated_date()}}) # on met a jour l'heure
            self.players_table.update_one({"_id":str(id_guild)},{"$set":{"players."+str(id_user)+".number_of_rolls":1}}) # on reset le nombre de rolls

            return data.get("level",1)-1
    
        if data.get("number_of_rolls",0)<data.get("level",1): # sinon si il reste des rolls
            self.players_table.update_one({"_id":str(id_guild)},{"$inc":{"players."+str(id_user)+".number_of_rolls":1}}) # on incremente le nombre de roll
        return data.get("level",1)-(data.get("number_of_rolls",0)+1)


    def roll(self, id_guild : int ,id_user : int, test : bool = False) -> list[discord.Embed]: 
        if not self.can_roll(id_guild, id_user) and not test: return fbot.embed_wait()

        nb_remaining_roll=self.update_roll(id_guild, id_user)

        rolled=Cards.random_card()

        self.add_card(id_guild, id_user, rolled["id"])

        embed=Cards.get_embed_card(rolled["id"]).set_footer(text=f"Il reste {nb_remaining_roll}")

        return embed

    

    def add_card(self, id_guild : int, id_user : int, id_card : int, quantity : int  = 1) -> None: 
        """
        Ajoute une carte a la collection du joueur
        """

        updated_quantity=self.get_player_data(id_guild, id_user).get("cards",{}).get(str(id_card),0)+quantity

        if updated_quantity>0:
            self.players_table.update_one({"_id":str(id_guild)},{"$set":{"players."+str(id_user)+".cards."+str(id_card):updated_quantity}})
        else:
            self.players_table.update_one({"_id":str(id_guild)},{"$unset":{"players."+str(id_user)+".cards."+str(id_card):1}})

        # data= self.players_table.find_one({"_id":str(id_user)})
        # updated_quantity=data.get("cards",{}).get(str(id_card),0)+quantity
        # # updated_quantity=data["cards"][str(id_card),0]+quantity
        # if updated_quantity>0:
        #     self.players_table.update_one({"_id":str(id_user)}, {"$set":{"cards."+str(id_card):updated_quantity}})
        # else:
        #     self.players_table.update_one({"_id":str(id_user)}, {"$unset":{"cards."+str(id_card):1}})

    def list_of_cards(self, id_guild : int, id_user : int) -> list: 
        """
        Retourne la liste d'embed correspondant aux cartes du joueur
        """

        data= self.get_player_data(id_guild, id_user)

        cards=data.get("cards",{})

        return sorted(list(cards.items()), key=lambda x:int(x[0]))


    def affiche(self) -> list:
        """
        Affiche et renvoie la base de donnée sour forme de liste
        """
        for i in self.players_table.find():
            print(i)
        return [i for i in self.players_table.find()]
    

    def set_player_color(self, id_guild : int, id_user : int, color : str) -> None:
        self.players_table.update_one({"_id":str(id_guild)},{"$set":{"players."+str(id_user)+".color":color}})

    def add_money(self, id_guild : int, id_user : int, amount : int) -> None:
        self.get_player_data(id_guild, id_user)
        self.players_table.update_one({"_id":str(id_guild)},{"$inc":{"players."+str(id_user)+".money":amount}})





