import discord

from database.PlayerDB import PlayerDatabase

from data.Cards import Cards

p=PlayerDatabase()

class CollectionView(discord.ui.View): 
    def __init__(self, list_of_cards):
        super().__init__()
        self.list=list_of_cards
        self.n=0

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, emoji="⬅️") # Create a button
    async def previous_card(self, interaction, button):
        self.n-=1
        self.n%=len(self.list)
        await self.refresh(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, emoji="➡️") # Create a button
    async def next_card(self, interaction, button):
        self.n+=1
        self.n%=len(self.list)
        await self.refresh(interaction)

    async def refresh(self, interaction):
        if type(self.list[self.n])==int:
            await interaction.response.edit_message(embed=Cards.get_embed_card(self.list[self.n]).set_footer(text=f"{self.n+1}/{len(self.list)}"))
        else:
            await interaction.response.edit_message(embed=Cards.get_embed_card(self.list[self.n][0], self.list[self.n][1]).set_footer(text=f"{self.n+1}/{len(self.list)}"))
    
