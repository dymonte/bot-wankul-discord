from database.PlayerDB import PlayerDatabase

from data.Cards import Cards

import discord

import fbot



original_player_data={"last_roll":(0,0,0), "gold":100000, "level":2, "color":"#ffffff", "number_of_rolls":0, "stock":5, "cards":{}}


class Player(PlayerDatabase):

    def __init__(self, guild_id : int, user_id : int) -> None:
        super().__init__()

        self.guild_id=guild_id
        self.user_id=user_id

        self.data=self.get_player_data()
    
    def get_player_data(self)->dict:
        """
        Renvoie les informations du joueur sour forme d'un dictionnaire, 
        * si l'entrée dans la base de données n'existe pas, elle l'initialise avec des valeurs par défaut
        """

        guild_data=self.players_table.find_one({"_id":str(self.guild_id)})
        
        if guild_data==None:
            guild_data={"_id":str(self.guild_id), "players":{}}
            self.players_table.insert_one(guild_data)

        player_data=guild_data.get("players",{}).get(str(self.user_id),{})
        if player_data=={}:
            player_data=original_player_data
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id):player_data}})
        return player_data
    

    def can_roll(self) -> bool:
        """
        Renvoie si le joueur peut roll
        """

        
        if fbot.formated_date()==self.data.get("last_roll",(0,0,0)):
            return self.data.get("number_of_rolls",0)<(self.data.get("level",1)+fbot.default_nb_rolls) 
        return True

    def update_roll(self) -> int:
        """
        Met a jour la base de donnée pour le roll et renvoie le nombre de rolls restants

        """

        if fbot.formated_date()!=self.data.get("last_roll",(0,0,0)): # si l'heure a changée depuis le dernier roll
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id)+".last_roll":fbot.formated_date()}}) # on met a jour l'heure
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id)+".number_of_rolls":1}}) # on reset le nombre de rolls

            return (self.data.get("level",0)+fbot.default_nb_rolls)-1
    
        if self.data.get("number_of_rolls",0)<(self.data.get("level",0)+fbot.default_nb_rolls): # sinon si il reste des rolls
            self.players_table.update_one({"_id":str(self.guild_id)},{"$inc":{"players."+str(self.user_id)+".number_of_rolls":1}}) # on incremente le nombre de roll
        return (self.data.get("level",0)+fbot.default_nb_rolls)-(self.data.get("number_of_rolls",0)+1)


    def roll(self) -> discord.Embed: 
        stock=self.get_stock()
        can_roll=self.can_roll()
        if not can_roll and stock==0: 
            return fbot.embed_wait()

        elif can_roll:
            nb_remaining_roll=self.update_roll()
    
        else:
            self.add_stock(-1)
            nb_remaining_roll=0

        rolled=Cards.random_card()

        self.add_card(rolled["id"])

        embed=Cards.get_embed_card(rolled["id"]).set_footer(text=f"Restants : {nb_remaining_roll}"+(f" (+{self.get_stock()} en stock)" if self.get_stock()>0 else ""))

        return embed
    

    def add_card(self, id_card : int, quantity : int  = 1) -> None: 
        """
        Ajoute une carte a la collection du joueur
        """

        updated_quantity=self.data.get("cards",{}).get(str(id_card),0)+quantity

        if updated_quantity>0:
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id)+".cards."+str(id_card):updated_quantity}})
        else:
            self.players_table.update_one({"_id":str(self.guild_id)},{"$unset":{"players."+str(self.user_id)+".cards."+str(id_card):1}})


    def list_of_cards(self) -> list: 
        """
        Retourne la liste d'embed correspondant aux cartes du joueur
        """
        cards=self.data.get("cards",{})

        return sorted(list(cards.items()), key=lambda x:int(x[0]))


    def set_player_color(self, color : str) -> None:
        self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id)+".color":color}})
        self.data["color"]=color

    def get_player_color(self) -> str:
        return self.data.get("color","#000000")
    
    def add_gold(self, amount : int) -> None:
        self.data["gold"]+=amount
        self.players_table.update_one({"_id":str(self.guild_id)},{"$inc":{"players."+str(self.user_id)+".gold":amount}})

    def get_lvl(self) -> int:
        return self.data.get("level",0)

    def add_lvl(self, amount : int = 1) -> None:
        self.data["level"]+=amount
        self.players_table.update_one({"_id":str(self.guild_id)},{"$inc":{"players."+str(self.user_id)+".level":amount}})

    def get_gold(self) -> int:
        return self.data.get("gold",0)
    
    def get_stock(self) -> int:
        return self.data.get("stock",0)

    def add_stock(self, amount : int) -> None:
        self.data["stock"]+=amount
        self.players_table.update_one({"_id":str(self.guild_id)},{"$inc":{"players."+str(self.user_id)+".stock":amount}})