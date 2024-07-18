import discord

import database.Player as Player

from data.Cards import Cards

p=Player.PlayerDatabase()


class SellView(discord.ui.View):

    def __init__(self, inte: discord.Interaction, guild_id : int, id_user : int, list_cards : list, value : int, embed: discord.Embed) -> None:
        super().__init__()

        self.inte=inte
        self.value=value
        self.guild_id=guild_id
        self.id_user=id_user
        self.list_cards=list_cards
        self.embed=embed

        for id_card, quantity in list_cards:
            p.add_card(inte.guild.id, inte.user.id, int(id_card), -1*int(quantity))


    @discord.ui.button(label="Vendre", style=discord.ButtonStyle.success, custom_id="sell")
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id!=self.id_user:
            await interaction.response.defer()
            return
        
        p.add_gold(self.guild_id, self.id_user, self.value)

        self.embed.set_field_at(0,name=f"Vendue par {interaction.user.name} pour {self.value} gold{'s' if self.value>1 else ''}.", value=Cards.formated_to_str(self.list_cards), inline=False)
        self.embed.color=discord.Color.green()
        await self.inte.edit_original_response(embed=self.embed, view=None)
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.danger, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id!=self.id_user:
            await interaction.response.defer()
            return
        
        for id_card, quantity in self.list_cards:
            p.add_card(self.guild_id, self.id_user, int(id_card), int(quantity))
        self.embed.set_field_at(0,name=f"Annulee par {interaction.user.name}", value=Cards.formated_to_str(self.list_cards), inline=False)
        self.embed.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed, view=None)
        self.stop()

    async def on_timeout(self) -> None:
        for id_card, quantity in self.list_cards:
            p.add_card(self.guild_id, self.id_user, int(id_card), int(quantity))
        self.stop()