import discord

import fbot

import database.PlayerDB as PlayerDB

from database.Player import Player

p=PlayerDB.PlayerDatabase()


class ShopView(discord.ui.View):
    """
    Gere la vue du magasin

    inte : l'intéraction de la commande
    player : le joueur
    embed : l'embed par defaut
    """

    def __init__(self, inte: discord.Interaction, player : Player, embed : discord.Embed):
        super().__init__()

        self.inte=inte
        self.player=player
        self.embed=embed


    @discord.ui.button(emoji="💎", style=discord.ButtonStyle.success, custom_id="lvlUp")
    async def lvlUp(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.player.refresh_data()
        player_level=self.player.get_lvl()
        player_gold=self.player.get_gold()

        if player_level<fbot.maxLvl and self.player.get_gold()>=fbot.shop_prices["lvlUp"][player_level+1]:
            self.player.add_gold(-1*fbot.shop_prices["lvlUp"][player_level+1])
            self.player.add_lvl()

            player_level=self.player.get_lvl()

            player_gold=self.player.get_gold()


            self.embed=fbot.embed_shop(player_level, self.player.get_stock(), player_gold)

            self.embed.set_footer(text="+1 level")

        elif player_level>=fbot.maxLvl:
            self.embed.set_footer(text="LVL maximum atteint")

        else:
            self.embed.set_footer(text="Pas assez de gold")

        await interaction.response.edit_message(embed=self.embed)



    @discord.ui.button(emoji="🃏", style=discord.ButtonStyle.success, custom_id="buyCards")
    async def buyCards(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.player.refresh_data()
        if self.player.get_gold()>=30:
            self.player.add_gold(-30)
            self.player.add_stock(3)

            self.embed.set_field_at(1,name="🃏 **Acheter 3 cartes** (🪙30)", value=f"Achetez des stocks de roll supplémentaires\nVous avez actuellement {self.player.get_stock()} en stock", inline=False)

            self.embed.set_footer(text="+3 cartes en stock")
        else:
            self.embed.set_footer(text="Pas assez de gold")
        
        self.embed.title=f"**Shop** - 🪙 {self.player.get_gold()}"
        await interaction.response.edit_message(embed=self.embed)


