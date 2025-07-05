import discord

from database.Player import Player

from data.Cards import Cards




class SellView(discord.ui.View):
    """
    ! ATTENTION : problème de verification des cartes, voir Views/Trade.py
    """

    def __init__(self, inte: discord.Interaction, player : Player, list_cards : list, value : int, embed: discord.Embed) -> None:
        """
        Initializes the SellView with interaction details, player information, 
        list of cards to be sold, their total value, and an embed for display.

        Args:
            inte (discord.Interaction): The interaction object for the command.
            player (Player): The player instance performing the sell.
            list_cards (list): A list of cards and their quantities to be sold.
            value (int): The total value of the cards in gold.
            embed (discord.Embed): The embed object to display the sell information.
        """

        super().__init__()

        self.inte=inte
        self.value=value
        self.player=player
        self.list_cards=list_cards
        self.embed=embed



    @discord.ui.button(label="Vendre", style=discord.ButtonStyle.success, custom_id="sell")
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Handles the "Vendre" button interaction.

        If the user is not the original player, the interaction is deferred.
        If a card is missing from the player's inventory, an error message is displayed.
        Otherwise, the cards are removed from the player's inventory, and the gold is added.
        The embed is updated to reflect the success of the transaction, and the view is stopped.
        """
        if interaction.user.id!=self.player.user_id:
            await interaction.response.defer()
            return
        
        for id_card, quantity in self.list_cards:
            if not self.player.has(int(id_card), int(quantity)):
                await self.cancel_sell("Il manque une carte.")
                return
            
        for id_card, quantity in self.list_cards: #retirer les cartes
            self.player.add_card(int(id_card), -1*int(quantity))
        self.player.add("gold",self.value) # ajouter l'argent

        self.embed.set_footer(text=f"Accepté pour {self.value} 🪙")
        self.embed.color=discord.Color.green()
        await self.inte.edit_original_response(embed=self.embed, view=None, delete_after=10)
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.danger, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Handles the "Annuler" button interaction.

        If the user is not the original player, the interaction is deferred.
        Otherwise, the transaction is canceled, and the embed is updated to reflect the cancellation.
        """
        if interaction.user.id!=self.player.user_id:
            await interaction.response.defer()
            return
        
        await self.cancel_sell("Annulation de la transaction.")
    
    async def cancel_sell(self, message : str) -> None:
        """
        Cancel the sell transaction.

        Args:
            message (str): The message to display as the footer of the embed.

        Sets the embed color to red, sets the footer with the given message, and stops the view.
        """
        self.embed.color=discord.Color.red()
        self.embed.set_footer(text=message)
        await self.inte.edit_original_response(embed=self.embed, view=None, delete_after=10)
        self.stop()
        
    async def on_timeout(self) -> None:
        """
        Handles the timeout of the view.

        Sets the embed color to grey, sets the footer with a "Temps écoulé" message, and stops the view.
        """
        self.embed.set_footer(f"Temps écoulé")
        self.embed.color=discord.Color.greyple()
        await self.inte.edit_original_response(embed=self.embed, view=None, delete_after=10)
        self.stop()