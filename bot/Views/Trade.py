import discord

from data.Cards import Cards
import fbot

from database.Player import Player

import database.PlayerDB as PlayerDB

p=PlayerDB.PlayerDatabase()


class TradeAcceptView(discord.ui.View):

    def __init__(self, inte: discord.Interaction, guild_id : int, list_cards_usr1 : list, money_usr1 : int, player1 : Player, list_cards_usr2 : list, money_usr2 : int, player2 : Player, embed_trade : discord.Embed) -> None:
        """
        Initialize a TradeAcceptView object.

        Args:
            inte (discord.Interaction): The interaction object for the command.
            guild_id (int): The Discord guild ID.
            list_cards_usr1 (list): The list of cards to be traded by user 1.
            money_usr1 (int): The amount of gold to be traded by user 1.
            player1 (Player): The player instance for user 1.
            list_cards_usr2 (list): The list of cards to be traded by user 2.
            money_usr2 (int): The amount of gold to be traded by user 2.
            player2 (Player): The player instance for user 2.
            embed_trade (discord.Embed): The embed object to display the trade information.

        Returns:
            None
        """
        super().__init__()


        self.inte=inte

        self.guild_id=guild_id

        self.list_cards_usr1=list_cards_usr1
        self.list_cards_usr2=list_cards_usr2

        self.money_usr1=money_usr1
        self.money_usr2=money_usr2


        self.player1=player1
        self.player2=player2
        self.id_user1=player1.user_id
        self.id_user2=player2.user_id
        
        self.embed_trade=embed_trade

        self.usr1_accepted=False
        self.usr2_accepted=False

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green, custom_id="accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: 
        """
        Handles the "Accepter" button interaction.

        If the user is not one of the two players involved in the trade, the interaction is deferred.
        If the user is player 1, the trade information for player 1 is updated to reflect the acceptance.
        If the user is player 2, the trade information for player 2 is updated to reflect the acceptance.
        If both players have accepted, the trade is validated.
        """
        if interaction.user.id!=self.id_user1 and interaction.user.id!=self.id_user2:
            await interaction.response.defer()
            return
        
        if interaction.user.id==self.id_user1:
            self.usr1_accepted=True
            format1=await Cards.formated_to_str(self.list_cards_usr1)
            self.embed_trade.set_field_at(0,name=f"Accepté par {interaction.user.name}", value=f"{format1 if format1!="" else "(vide)"} + {self.money_usr1} 🪙", inline=False)
            await self.inte.edit_original_response(embed=self.embed_trade)
            await interaction.response.defer()

        else:
            self.usr2_accepted=True
            format2=await Cards.formated_to_str(self.list_cards_usr2)
            self.embed_trade.set_field_at(1,name=f"Accepté par {interaction.user.name}", value=f"{format2 if format2!="" else "(vide)"} + {self.money_usr2} 🪙", inline=False)
            await self.inte.edit_original_response(embed=self.embed_trade)
            await interaction.response.defer()

        if self.usr1_accepted and self.usr2_accepted:
            await self.validate_trade(interaction)
        
        

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red, custom_id="refuse")
    async def refuse(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Handles the "Refuser" button interaction.

        If the user is not one of the two players involved in the trade, the interaction is ignored.
        Otherwise, the trade is canceled, and a message indicating the user's refusal is displayed.
        """

        if interaction.user.id!=self.id_user1 and interaction.user.id!=self.id_user2: return
        
        await self.cancel_trade(cause=f"refus de {interaction.user.name}")

    async def validate_trade(self, interaction: discord.Interaction) -> None:
        """
        Validates and executes the trade between two players.

        This method checks if both players have the necessary cards and gold 
        to proceed with the trade. If any card is missing or if either player 
        lacks sufficient gold, the trade is canceled. On successful validation, 
        the specified amounts of gold and cards are exchanged between the players, 
        and the trade embed is updated to reflect the success.

        Args:
            interaction (discord.Interaction): The interaction object for the trade.

        Returns:
            None
        """

        self.player1.refresh_data()
        self.player2.refresh_data()
        
        for card in self.list_cards_usr1: #verifier que les cartes sont encore en sa possesion sinon annuler (avec nouvel appel bdd)
            if not self.player1.has(card[0], card[1]):
                await self.cancel_trade(cause="une carte est manquante")
                return
        for card in self.list_cards_usr2:
            if not self.player2.has(card[0], card[1]):
                await self.cancel_trade(cause="une carte est manquante")
                return 

        if self.money_usr1>self.player1.get("gold") or self.money_usr2>self.player2.get("gold"):
            await self.cancel_trade(cause="il manque de l'argent")
            return

        self.player1.add("gold",-1*self.money_usr1)
        self.player2.add("gold",-1*self.money_usr2)

        self.player1.add("gold",self.money_usr2)
        self.player2.add("gold",self.money_usr1)

        for card in self.list_cards_usr1:
            self.player1.add_card(card[0], -1*card[1]) # retire la carte de l'utilisateur
            self.player2.add_card(card[0], card[1]) # ajoute la carte à l'autre utilisateur
        for card in self.list_cards_usr2:
            self.player2.add_card(card[0], -1*card[1])
            self.player1.add_card(card[0], card[1])

    
        self.embed_trade.set_footer(text="Accepté")
        self.embed_trade.color=discord.Color.green()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        self.stop()

    async def cancel_trade(self, cause : str = "") -> None:
        """
        Cancel the trade.

        This method updates the trade embed to reflect the cancellation, by setting its color to red and its footer to a message indicating the cause of the cancellation (if any).

        Args:
            cause (str): The cause of the cancellation. Defaults to an empty string.

        Returns:
            None
        """
        self.embed_trade.set_footer(text=f"Annulé{" : " if cause!="" else ""}{cause}")
        self.embed_trade.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        self.stop()

    async def on_timeout(self) -> None:
        """
        Handles the timeout of the trade interaction.

        This method updates the trade embed to reflect the cancellation due to timeout,
        by setting its color to red and its footer to indicate the trade was canceled.
        Stops the view once the changes are made.
        """

        self.embed_trade.set_footer(text="Annulé")
        self.embed_trade.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        self.stop()
