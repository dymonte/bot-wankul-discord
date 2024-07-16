import discord

import data.Cards
import fbot

import database.Player as Player

p=Player.PlayerDatabase()


class TradeAcceptView(discord.ui.View):

    def __init__(self, inte: discord.Interaction, list_cards_usr1 : list, id_user1 : int, list_cards_usr2 : list, id_user2 : int, embed_trade : discord.Embed) -> None:
        super().__init__()


        self.inte=inte

        self.list_cards_usr1=list_cards_usr1
        self.list_cards_usr2=list_cards_usr2
        self.id_user1=id_user1
        self.id_user2=id_user2
        
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
            self.embed_trade.set_field_at(0,name=f"Accepté par {interaction.user.mention}", value=self.list_cards_usr1, inline=False)
            await self.inte.edit_original_response(embed=self.embed_trade)
            await interaction.response.defer()

        else:
            self.usr2_accepted=True
            self.embed_trade.set_field_at(1,name=f"Accepté par {interaction.user.mention}", value=self.list_cards_usr2, inline=False)
            await self.inte.edit_original_response(embed=self.embed_trade)
            interaction.response.defer()

        if self.usr1_accepted and self.usr2_accepted:
            self.embed_trade.set_footer(text="Accepté")
            self.embed_trade.color=discord.Color.green()
            await self.inte.edit_original_response(embed=self.embed_trade)
            for card in self.list_cards_usr1:
                p.add_card(self.id_user1, card[0], -1*card[1])
                p.add_card(self.id_user2, card[0], card[1])
            
            for card in self.list_cards_usr2:
                p.add_card(self.id_user2, card[0], -1*card[1])
                p.add_card(self.id_user1, card[0], card[1])
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
        self.stop()



    async def on_timeout(self) -> None:
        """
        TODO : effacer les boutons à la fin de l'echange, changer la couleur de l'embed et le footer
        """
        self.usr1_accepted=False
        self.usr2_accepted=False
        self.stop()
    #     self.text_input = discord.ui.TextInput(label="Entrez votre texte", placeholder="Entrez votre texte ici", custom_id="my_text_input")


    # async def on_submit(self, interaction: discord.Interaction):
    #     await interaction.response.send_message("Done")