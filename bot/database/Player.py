from database.PlayerDB import PlayerDatabase

from data.Cards import Cards

import discord

import utils as utils



original_player_data={"last_roll":(0,0,0), "gold":0, "level":0, "color":"#ffffff", "number_of_rolls":0, "stock":5, "wish":0, "cards":{}}


class Player(PlayerDatabase):

    def __init__(self, guild_id : int, user_id : int) -> None:
        """
        Initialize a Player object.

        Args:
            guild_id (int): The Discord guild ID.
            user_id (int): The Discord user ID.

        Returns:
            None
        """
        super().__init__()

        self.guild_id=guild_id
        self.user_id=user_id

        self.refresh_data()
    
    def get_player_data(self)->dict:
        """
        Retrieves the player data for the current user from the database.
        
        If the guild or player data does not exist in the database, initializes 
        them with default values and inserts/updates the database accordingly.

        Returns:
            dict: A dictionary containing the player's data.
        """

        guild_data=self.players_table.find_one({"_id":str(self.guild_id)})
        
        if guild_data==None: # si la guild n'existe pas
            guild_data={"_id":str(self.guild_id), "players":{}} # on l'ajoute
            self.players_table.insert_one(guild_data)

        player_data=guild_data.get("players",{}).get(str(self.user_id),{})
        if player_data=={}: # si le joueur n'existe pas
            player_data=original_player_data
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id):player_data}}) # ajout des valeurs pas defaut
        return player_data
    

    def can_roll(self) -> bool:
        """
        Checks if the player can roll.

        The player can roll if the number of rolls done this hour is less than the
        maximum number of rolls available (which is the player's level plus the
        default number of rolls).

        If the hour has changed since the last roll, the player can roll again.

        Returns:
            bool: True if the player can roll, False otherwise.
        """
        if utils.formated_date()==self.data.get("last_roll",(0,0,0)):
            return self.data.get("number_of_rolls",0)<(self.data.get("level",1)+utils.default_nb_rolls) 
        return True

    def update_roll(self) -> int:
        """
        Updates the player's roll counter.

        If the hour has changed since the last roll, the player's roll counter is
        reset and the hour is updated.

        If the player's roll counter is less than the maximum number of rolls
        available, the counter is incremented.

        Returns:
            int: The number of remaining rolls.
        """
        
        if utils.formated_date()!=self.data.get("last_roll",(0,0,0)): # si l'heure a changée depuis le dernier roll
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id)+".last_roll":utils.formated_date()}}) # on met a jour l'heure
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id)+".number_of_rolls":1}}) # on reset le nombre de rolls

            return (self.data.get("level",0)+utils.default_nb_rolls)-1
    
        if self.data.get("number_of_rolls",0)<(self.data.get("level",0)+utils.default_nb_rolls): # sinon si il reste des rolls
            self.players_table.update_one({"_id":str(self.guild_id)},{"$inc":{"players."+str(self.user_id)+".number_of_rolls":1}}) # on incremente le nombre de roll
        return (self.data.get("level",0)+utils.default_nb_rolls)-(self.data.get("number_of_rolls",0)+1)


    async def roll(self) -> discord.Embed: 
        """
        Performs a card roll for the player and returns an embed with the rolled card.

        The function checks if the player can roll based on their current roll count and stock.
        If the player can roll, it updates their roll count; if not, it reduces the stock.
        A random card is rolled, added to the player's collection, and an embed is generated
        with the card's details and the number of remaining rolls. If the rolled card matches
        the player's wish, gold is awarded and added to the player's balance.

        Returns:
            discord.Embed: An embed containing the details of the rolled card, or None if
            the player cannot roll and has no stock left.
        """

        stock=self.get("stock")
        can_roll=self.can_roll()
        if not can_roll and stock==0: 
            return None

        elif can_roll:
            nb_remaining_roll=self.update_roll()
    
        else:
            self.add("stock",-1)
            nb_remaining_roll=0

        rolled=await Cards.random_card()

        self.add_card(rolled["id"])

        embed=(await Cards.get_embed_card(rolled["id"])).set_footer(text=f"Restants : {nb_remaining_roll}"+(f" (+{self.get("stock")} en stock)" if self.get("stock")>0 else "")) # affiche le nombre de rolls restants et le stock au bas de l'embed

        if rolled["id"]==self.get("wish"):
            earning=int(100*utils.cost_per_rarity.get(rolled.get("rarity",{}).get("id",0),0))
            embed.add_field(name="Wish gagné", value=f"+ {earning} 🪙", inline=False)
            self.add("gold",earning)

        return embed
    

    def add_card(self, id_card : int, quantity : int  = 1) -> None: 
        """
        Adds a certain quantity of a card to the player's collection.

        Args:
            id_card (int): The id of the card to add.
            quantity (int, optional): The quantity of the card to add. Defaults to 1.

        Returns:
            None
        """
        self.refresh_data()

        updated_quantity=self.data.get("cards",{}).get(str(id_card),0)+quantity

        if updated_quantity>0:
            self.players_table.update_one({"_id":str(self.guild_id)},{"$set":{"players."+str(self.user_id)+".cards."+str(id_card):updated_quantity}})
        else:
            self.players_table.update_one({"_id":str(self.guild_id)},{"$unset":{"players."+str(self.user_id)+".cards."+str(id_card):1}})
            


    def list_of_cards(self) -> list: 
        """
        Returns a sorted list of all the cards in the player's collection.

        The list is a list of tuples, where the first element of each tuple is the id of the card
        and the second element is the quantity of the card in the player's collection.

        Returns:
            list: A sorted list of all the cards in the player's collection
        """
        cards=self.data.get("cards",{})

        return sorted(list(cards.items()), key=lambda x:int(x[0]))
    
    def update(self, action: str,field: str, amount: int = 1) -> bool:
        """
        Updates the player's data with the given action and value.

        Args:
            action (str): The action to perform. Can be "inc" to increment the value, or "set" to set the value.
            field (str): The field to update. Can be "gold", "stock", "level", or "wish".
            amount (int, optional): The amount to update the field by. Defaults to 1.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if action not in ["inc","set"]:
            return False
        
        query = {f"${action}": {f"players.{self.user_id}.{field}": amount}}

        try:
            self.players_table.update_one(
                    {"_id": str(self.guild_id)},
                    query)
            
            self.data[field] = self.data.get(field, 0) + amount if action == "inc" else amount
        
        except:
            raise Exception("Error updating player data")

        return True
    
    def add(self, field, amount : int = 0) -> bool:
        """
        Increments the player's given field by the given amount.

        Args:
            field (str): The field to increment. Can be "gold", "stock", "level", or "wish".
            amount (int, optional): The amount to increment the field by. Defaults to 0.

        Returns:
            bool: True if the increment was successful, False otherwise.
        """
        return self.update("inc", field, amount)

    def set(self, field, amount : int) -> bool:
        """
        Sets the player's given field to the given amount.

        Args:
            field (str): The field to set. Can be "gold", "stock", "level", or "wish".
            amount (int): The value to set the field to.

        Returns:
            bool: True if the set was successful, False otherwise.
        """
        return self.update("set", field, amount)
    
    def get(self, field):
        """
        Gets the value of the given field from the player's data.

        Args:
            field (str): The field to get. Can be "gold", "stock", "level", or "wish".

        Returns:
            any: The value of the given field or False if it does not exist.
        """
        return self.data.get(field,False)
    
    def has(self, id_card : int, quantity : int) -> bool:
        """
        Checks if the player has the given card with the given quantity.

        Args:
            id_card (int): The id of the card to check.
            quantity (int): The quantity of the card to check.

        Returns:
            bool: True if the player has the card with the given quantity, False otherwise.
        """
        self.refresh_data()
        return self.data.get("cards",{}).get(str(id_card),0)>=quantity
    
    def refresh_data(self) -> None:
        """
        Refreshes the player's data by re-fetching it from the database.

        This should be called before any operation that needs the player's data to be up-to-date.
        """
        self.data=self.get_player_data()