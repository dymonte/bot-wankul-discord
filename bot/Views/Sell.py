import discord

from database.Player import Player

from data.Cards import Cards




class SellView(discord.ui.View):
    """
    ! ATTENTION : problème de verification des cartes, voir Views/Shop.py
    """

    def __init__(self, inte: discord.Interaction, player : Player, list_cards : list, value : int, embed: discord.Embed) -> None:
        super().__init__()

        self.inte=inte
        self.value=value
        self.player=player
        self.list_cards=list_cards
        self.embed=embed

        for id_card, quantity in list_cards:
            self.player.add_card(int(id_card), -1*int(quantity))


    @discord.ui.button(label="Vendre", style=discord.ButtonStyle.success, custom_id="sell")
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id!=self.player.user_id:
            await interaction.response.defer()
            return
        
        self.player.add("gold",self.value)

        self.embed.set_field_at(0,name=f"Vendus par {interaction.user.name} pour {self.value} gold{'s' if self.value>1 else ''}.", value=await Cards.formated_to_str(self.list_cards), inline=False)
        self.embed.color=discord.Color.green()
        await self.inte.edit_original_response(embed=self.embed, view=None)
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.danger, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id!=self.player.user_id:
            await interaction.response.defer()
            return
        
        for id_card, quantity in self.list_cards:
            self.player.add_card(int(id_card), int(quantity))
        self.embed.set_field_at(0,name=f"Annulé par {interaction.user.name}.", value=await Cards.formated_to_str(self.list_cards), inline=False)
        self.embed.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed, view=None)
        self.stop()

    async def on_timeout(self) -> None:
        for id_card, quantity in self.list_cards:
            self.player.add_card(int(id_card), int(quantity))
        self.embed.set_field_at(0,name=f"Temps écoulé", value=await Cards.formated_to_str(self.list_cards), inline=False)
        self.embed.color=discord.Color.greyple()
        await self.inte.edit_original_response(embed=self.embed, view=None)
        self.stop()