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

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green, custom_id="accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None: # TODO : effacer les boutons à la fin de l'echange
        if interaction.user.id!=self.id_user1 and interaction.user.id!=self.id_user2:
            await interaction.response.defer()
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
            await interaction.response.defer()

        if self.usr1_accepted and self.usr2_accepted:
            await self.validate_trade(interaction)
        
        

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red, custom_id="refuse")
    async def refuse(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        * Ferme le trade dans le cas du refus de l'un des deux
        TODO : effacer les boutons à la fin de l'echange, changer la couleur de l'embed et le footer
        """
        if interaction.user.id!=self.id_user1 and interaction.user.id!=self.id_user2: return
        
        await self.cancel_trade(cause=f"refus de {interaction.user.name}")


    async def validate_trade(self, interaction: discord.Interaction) -> None:

        #! ATTENTION, PROBELEME D'ORDRE VERIF DOIT ETRE AVANT ECHANGE
        for card in self.list_cards_usr1: #verifier que les cartes sont encore en sa possesion sinon annuler (avec nouvel appel bdd)
            if not self.player1.has(card[0], card[1]):
                await self.cancel_trade(cause="une carte est manquante")
                return
        for card in self.list_cards_usr2:
            if not self.player2.has(card[0], card[1]):
                await self.cancel_trade(cause="une carte est manquante")
                return 

        for card in self.list_cards_usr1:
            self.player1.add_card(card[0], -1*card[1]) # retire la carte de l'utilisateur
            self.player2.add_card(card[0], card[1]) # ajoute la carte à l'autre utilisateur
        for card in self.list_cards_usr2:
            self.player2.add_card(card[0], -1*card[1])
            self.player1.add_card(card[0], card[1])

    
        self.embed_trade.set_footer(text="Accepté")
        self.embed_trade.color=discord.Color.green()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        self.stop()

    async def cancel_trade(self, cause : str = "") -> None:
        self.embed_trade.set_footer(text=f"Annulé{" : " if cause!="" else ""}{cause}")
        self.embed_trade.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        self.stop()

    async def on_timeout(self) -> None:
        """
        TODO : changer la couleur de l'embed et le footer
        """
        self.embed_trade.set_footer(text="Annulé")
        self.embed_trade.color=discord.Color.red()
        await self.inte.edit_original_response(embed=self.embed_trade, view=None)
        self.stop()
