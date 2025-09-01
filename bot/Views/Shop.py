import discord

import utils as utils

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
        """
        Initializes the ShopView with interaction details, player information, 
        and an embed for display.

        Args:
            inte (discord.Interaction): The interaction object for the command.
            player (Player): The player instance interacting with the shop.
            embed (discord.Embed): The embed object to display the shop information.
        """
        super().__init__()

        self.inte=inte
        self.player=player
        self.embed=embed


    @discord.ui.button(emoji="💎", style=discord.ButtonStyle.success, custom_id="lvlUp")
    async def lvlUp(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Handles the level-up button interaction in the shop.

        This method checks if the player has enough gold to level up and if the player's
        level is below the maximum allowed level. If the player meets the requirements,
        the gold is deducted, and the player's level is incremented by one. The embed is
        updated to reflect the new level and gold amount. If the player has reached the
        maximum level or lacks sufficient gold, an appropriate message is set in the footer
        of the embed.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            button (discord.ui.Button): The button that triggered the interaction.

        Returns:
            None
        """

        self.player.refresh_data()
        player_level=self.player.get("level")
        player_gold=self.player.get("gold")


        if player_level<utils.maxLvl and self.player.get("gold")>=utils.shop_prices["lvlUp"][player_level+1]: # si le joueur a assez de gold et que le niveau n'est pas maximum
            self.player.add("gold", -1*utils.shop_prices["lvlUp"][player_level+1])
            self.player.add("level", 1)


            player_level=self.player.get("level")

            player_gold=self.player.get("gold")


            self.embed=utils.embed_shop(player_level, self.player.get("stock"), player_gold)

            self.embed.set_footer(text="+1 level")

        elif player_level>=utils.maxLvl:
            self.embed.set_footer(text="LVL maximum atteint")

        else:
            self.embed.set_footer(text="Pas assez de gold")

        await interaction.response.edit_message(embed=self.embed)



    @discord.ui.button(emoji="🃏", style=discord.ButtonStyle.success, custom_id="buyCards")
    async def buyCards(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Handles the "Acheter 3 cartes" button interaction.

        If the player has at least 30 gold, 30 gold is deducted from their balance,
        and 3 card stock is added to their inventory. The embed is updated to reflect
        the new stock and gold balance, and a success message is displayed in the footer.
        If the player lacks sufficient gold, an error message is displayed in the footer.
        
        Args:
            interaction (discord.Interaction): The interaction object for the command.
            button (discord.ui.Button): The button that triggered the interaction.
        
        Returns:
            None
        """

        self.player.refresh_data()
        if self.player.get("gold")>=30:
            self.player.add("gold",-30)
            self.player.add("stock",3)

            self.embed.set_field_at(1,name="🃏 **Acheter 3 cartes** (🪙 30)", value=f"Achetez des stocks de roll supplémentaires\nVous avez actuellement {self.player.get("stock")} en stock", inline=False)

            self.embed.set_footer(text="+3 cartes en stock")
        else:
            self.embed.set_footer(text="Pas assez de gold")
        
        self.embed.title=f"**Shop** - 🪙 {self.player.get("gold")}"
        await interaction.response.edit_message(embed=self.embed)

    async def on_timeout(self) -> None:
        """
        Handles the timeout of the shop view.
        """
        await self.inte.delete_original_response()
        self.stop()
