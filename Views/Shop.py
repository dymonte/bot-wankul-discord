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
        player_level=p.get_lvl(self.inte.guild.id, self.id_user)
        if p.get_money(self.inte.guild.id, self.id_user)>=fbot.shop_prices["lvlUp"] and player_level<fbot.maxLvl:
            p.add_money(self.inte.guild.id, self.id_user, -1*fbot.shop_prices["lvlUp"])
            p.add_lvl(self.inte.guild.id, self.id_user)

            player_level+=1
            self.embed.set_field_at(0,name="💎 Level Up *(🪙1000)*", value=f"Augmentez votre niveau\nVous êtes actuellement niveau {player_level}/5", inline=False)

            self.embed.set_footer(text="+1 level")
        elif p.get_money(self.inte.guild.id, self.id_user)<10:
            self.embed.set_footer(text="Pas assez de gold")
        else:
            self.embed.set_footer(text="LVL maximum atteint")
        
        self.embed.title=f"**Shop** - 🪙 {p.get_money(self.inte.guild.id, self.id_user)}"

        await interaction.response.edit_message(embed=self.embed)



    @discord.ui.button(emoji="🃏", style=discord.ButtonStyle.success, custom_id="buyCards")
    async def buyCards(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if p.get_money(self.inte.guild.id, self.id_user)>=30:
            p.add_money(self.inte.guild.id, self.id_user, -30)
            p.add_stock(self.inte.guild.id, self.id_user, 3)

            self.embed.set_footer(text="+3 cartes en stock")
        else:
            self.embed.set_footer(text="Pas assez de gold")
        
        self.embed.title=f"**Shop** - 🪙 {p.get_money(self.inte.guild.id, self.id_user)}"
        await interaction.response.edit_message(embed=self.embed)


