import discord

import data.Cards
import fbot

import database.Player as Player

from data.Cards import Cards

p=Player.PlayerDatabase()


class ShopView(discord.ui.View):

    def __init__(self, inte: discord.Interaction, id_user : int, embed : discord.Embed):
        super().__init__()

        self.inte=inte
        self.id_user=id_user
        self.embed=embed


    @discord.ui.button(emoji="💎", style=discord.ButtonStyle.success, custom_id="lvlUp")
    async def lvlUp(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        player_data=p.get_player_data(self.inte.guild.id, self.id_user)
        player_level=player_data.get("level",0)
        player_gold=player_data.get("gold",0)

        if player_level<fbot.maxLvl and p.get_gold(self.inte.guild.id, self.id_user)>=fbot.shop_prices["lvlUp"][player_level+1]:
            p.add_gold(self.inte.guild.id, self.id_user, -1*fbot.shop_prices["lvlUp"][player_level+1])
            p.add_lvl(self.inte.guild.id, self.id_user)

            player_level+=1

            player_gold-=fbot.shop_prices["lvlUp"][player_level]


            self.embed=fbot.embed_shop(player_level, player_data.get("stock",0), player_gold)

            self.embed.set_footer(text="+1 level")

        elif p.get_gold(self.inte.guild.id, self.id_user)<10:
            self.embed.set_footer(text="Pas assez de gold")

        else:
            self.embed.set_footer(text="LVL maximum atteint")

        await interaction.response.edit_message(embed=self.embed)



    @discord.ui.button(emoji="🃏", style=discord.ButtonStyle.success, custom_id="buyCards")
    async def buyCards(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if p.get_gold(self.inte.guild.id, self.id_user)>=30:
            p.add_gold(self.inte.guild.id, self.id_user, -30)
            p.add_stock(self.inte.guild.id, self.id_user, 3)

            self.embed.set_footer(text="+3 cartes en stock")
        else:
            self.embed.set_footer(text="Pas assez de gold")
        
        self.embed.title=f"**Shop** - 🪙 {p.get_gold(self.inte.guild.id, self.id_user)}"
        await interaction.response.edit_message(embed=self.embed)


