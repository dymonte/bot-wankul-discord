from database.PlayerDB import PlayerDatabase

from data.Cards import Cards

import discord

import fbot



original_player_data={"last_roll":(0,0,0), "gold":100000, "level":0, "color":"#ffffff", "number_of_rolls":0, "stock":5, "wish":0, "cards":{}}


class Player(PlayerDatabase):

    def __init__(self, guild_id : int, user_id : int) -> None:
        super().__init__()

        self.guild_id=guild_id
        self.user_id=user_id

        self.refresh_data()
    
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


    async def roll(self) -> discord.Embed: 
        stock=self.get("stock")
        can_roll=self.can_roll()
        if not can_roll and stock==0: 
            return None

        elif can_roll:
            nb_remaining_roll=self.update_roll()
    
        else:
            self.add_stock(-1)
            nb_remaining_roll=0

        rolled=await Cards.random_card()

        self.add_card(rolled["id"])

        embed=(await Cards.get_embed_card(rolled["id"])).set_footer(text=f"Restants : {nb_remaining_roll}"+(f" (+{self.get("stock")} en stock)" if self.get("stock")>0 else "")) # affiche le nombre de rolls restants et le stock au bas de l'embed

        if rolled["id"]==self.get("wish"):
            earning=int(100*fbot.cost_per_rarity.get(rolled.get("rarity",{}).get("id",0),0))
            embed.add_field(name="Wish gagné", value=f"+ {earning} 🪙", inline=False)
            self.add("gold",earning)

        return embed
    

    def add_card(self, id_card : int, quantity : int  = 1) -> None: 
        """
        Ajoute une carte a la collection du joueur
        """
        
        self.refresh_data()

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
    
    def update(self, action: str,field: str, amount: int = 1) -> bool:
        """
        Met a jour le champ {field} du joueur

        Args:
            action (str): soit "inc" pour incrementer, soit "set" pour mettre a jour
            field (str): le nom du champ a mettre a jour
            amount (int, optional): la valeur a ajouter ou a affecter. Defaults to 1.

        Returns:
            bool: True si la mise a jour a reussi, False sinon
        """
        if action not in ["inc","set"]:
            return False
        
        query = {f"${action}": {f"players.{self.user_id}.{field}": amount}}

        try:
            self.player_table.update_one(
                    {"_id": str(self.guild_id)},
                    query)
            
            self.data[field] = self.data.get(field, 0) + amount if action == "inc" else amount
        
        except:
            return False

        return True
    
    def add(self, field, amount : int = 0) -> bool:
        return self.update("inc", field, amount)

    def set(self, field, amount : int) -> bool:
        return self.update("set", field, amount)
    
    def get(self, field):
        return self.data.get(field,False)
    
    def has(self, id_card : int, quantity : int) -> bool:
        self.refresh_data()
        return self.data.get("cards",{}).get(str(id_card),0)>=quantity
    
    def refresh_data(self) -> None:
        self.data=self.get_player_data()