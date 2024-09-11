import discord

from data.Cards import Cards
import fbot

from database.Player import Player

import database.PlayerDB as PlayerDB

p=PlayerDB.PlayerDatabase()


class TradeAcceptView(discord.ui.View):

    def __init__(self, inte: discord.Interaction, guild_id : int, list_cards_usr1 : list, player1 : Player, list_cards_usr2 : list, player2 : Player, embed_trade : discord.Embed) -> None:
        super().__init__()


        self.inte=inte

        self.guild_id=guild_id

        self.list_cards_usr1=list_cards_usr1
        self.list_cards_usr2=list_cards_usr2


        self.player1=player1
        self.player2=player2
        self.id_user1=player1.user_id
        self.id_user2=player2.user_id
        
        self.embed_trade=embed_trade

        self.usr1_accepted=False
        self.usr2_accepted=False

        for card in self.list_cards_usr1:
            player1.add_card(card[0], -1*card[1])

        for card in self.list_cards_usr2:
            player2.add_card(card[0], -1*card[1])

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green, custom_id="accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: # TODO : effacer les boutons à la fin de l'echange
        print(self.id_user1,interaction.user.id)
        if interaction.user.id!=self.id_user1 and interaction.user.id!=self.id_user2:
            await interaction.response.defer()
            print("Pas le bon utilisateur")
            return
        
        if interaction.user.id==self.id_user1:
            self.usr1_accepted=True
            self.embed_trade.set_field_at(0,name=f"Accepté par {interaction.user.name}", value=await Cards.formated_to_str(self.list_cards_usr1), inline=False)
            await self.inte.edit_original_response(embed=self.embed_trade)
            await interaction.response.defer()

        else:
            self.usr2_accepted=True
            self.embed_trade.set_field_at(1,name=f"Accepté par {interaction.user.name}", value=await Cards.formated_to_str(self.list_cards_usr2), inline=False)
            await self.inte.edit_original_response(embed=self.embed_trade)
            interaction.response.defer()

        if self.usr1_accepted and self.usr2_accepted:
            self.embed_trade.set_footer(text="Accepté")
            self.embed_trade.color=discord.Color.green()
            await self.inte.edit_original_response(embed=self.embed_trade, view=None)
            for card in self.list_cards_usr1:
                self.player2.add_card(card[0], card[1])
            
            for card in self.list_cards_usr2:
                self.player1.add_card(card[0], card[1])
            await interaction.response.defer()
            self.stop()
        
        

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red, custom_id="refuse")
    async def refuse(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        * Ferme le trade dans le cas du refus de l'un des deux
        TODO : effacer les boutons à la fin de l'echange, changer la couleur de l'embed et le footer
        """
        if interaction.user.id!=self.id_user1 and interaction.user.id!=self.id_user2:
            return
        
        self.embed_trade.set_footer(text=f"Refus de {interaction.user.name}")
        self.embed_trade.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        await interaction.response.defer()

        for card in self.list_cards_usr1:
            self.player1.add_card(card[0], card[1])

        for card in self.list_cards_usr2:
            self.player2.add_card(card[0], card[1])
        self.stop()



    async def on_timeout(self) -> None:
        """
        TODO : changer la couleur de l'embed et le footer
        """
        self.usr1_accepted=False
        self.usr2_accepted=False
        for card in self.list_cards_usr1:
            self.player1.add_card(card[0], card[1])

        for card in self.list_cards_usr2:
            self.player2.add_card(card[0], card[1])

        self.embed_trade.set_footer(text="Annulé")
        self.embed_trade.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        self.stop()
