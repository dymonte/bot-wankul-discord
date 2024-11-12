import discord

from database.Player import Player

from data.Cards import Cards




class SellView(discord.ui.View):
    """
    ! ATTENTION : problème de verification des cartes, voir Views/Trade.py
    """

    def __init__(self, inte: discord.Interaction, player : Player, list_cards : list, value : int, embed: discord.Embed) -> None:
        super().__init__()

        self.inte=inte
        self.value=value
        self.player=player
        self.list_cards=list_cards
        self.embed=embed



    @discord.ui.button(label="Vendre", style=discord.ButtonStyle.success, custom_id="sell")
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
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
        await self.inte.edit_original_response(embed=self.embed, view=None)
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.danger, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id!=self.player.user_id:
            await interaction.response.defer()
            return
        
        await self.cancel_sell("Annulation de la transaction.")
    
    async def cancel_sell(self, message : str) -> None:
        self.embed.color=discord.Color.red()
        self.embed.set_footer(text=message)
        await self.inte.edit_original_response(embed=self.embed, view=None)
        self.stop()
        
    async def on_timeout(self) -> None:
        self.embed.set_footer(f"Temps écoulé")
        self.embed.color=discord.Color.greyple()
        await self.inte.edit_original_response(embed=self.embed, view=None)
        self.stop()