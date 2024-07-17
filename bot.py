# --- Imports discord ---
import discord
from discord.ext import commands
from discord import app_commands


# --- Imports extern ---
import time, json


# --- Imports intern ---
import database.Player as Player, fbot
from Views.Collection import CollectionView
from Views.Trade import TradeAcceptView
from Views.Sell import SellView
from data.Cards import Cards




p=Player.PlayerDatabase() # p -> base de donnee des joueurs

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='-', intents=intents)

tree = bot.tree



@bot.event
async def on_ready():
    """
    Le bot se synchronise et affiche qu'il est connecte
    """
    await tree.sync()
    print(f'Connecte en tant que {bot.user.name}')
    print('Done')


@tree.command(name="roll", description="roll")
async def roll(inte : discord.Interaction):
    r=p.roll(inte.guild.id, inte.user.id)
    await inte.response.send_message(embed=r if r else fbot.embed_wait(), ephemeral=r==None)


@tree.command(name="drop", description="drop")
async def dr(inte : discord.Interaction):
    """
    TODO
    """
    p.drop_table()
    await inte.response.send_message("done", ephemeral=True)


@tree.command(name="collection", description="list")
async def cl(inte : discord.Interaction, user : discord.User = None, show : bool = True):
    id_user = user.id if user!=None else inte.user.id
    p.affiche()
    list_of_cards=p.list_of_cards(inte.guild.id, id_user)

    if len(list_of_cards)==0:
        await inte.response.send_message(content="aucune carte", ephemeral=True)
    elif len(list_of_cards)==1:
        await inte.response.send_message(ephemeral=not show, embed=Cards.get_embed_card(list_of_cards[0][0], list_of_cards[0][1]).set_footer(text="1/1"))
    else:
        await inte.response.send_message(ephemeral=not show, embed=Cards.get_embed_card(list_of_cards[0][0], list_of_cards[0][1]).set_footer(text=f"1/{len(list_of_cards)}"), view=CollectionView(list_of_cards))


@tree.command(name="info", description="Informations sur une carte")
async def cl(inte : discord.Interaction, id_card : int):
    await inte.response.send_message(embed=Cards.get_embed_card(id_card, detailed=True), ephemeral=True)


@tree.command(name="trade", description="exemple de format de trade : 125|1&18|2")
async def te(inte : discord.Interaction, user : discord.User, offre : str, demande : str):


    trade_usr1=Cards.format_list_card(offre, p.get_player_data(inte.guild.id, inte.user.id).get("cards",{}))
    trade_usr2=Cards.format_list_card(demande, p.get_player_data(inte.guild.id, user.id).get("cards",{}))    

    emebed_trade=discord.Embed(title="Trade")
    emebed_trade.add_field(name=f"En attente de {inte.user.name}", value=Cards.formated_to_str(trade_usr1), inline=False)
    emebed_trade.add_field(name=f"En attente de {user.name}", value=Cards.formated_to_str(trade_usr2), inline=False)
    print(Cards.formated_to_str(trade_usr1), Cards.formated_to_str(trade_usr2))

    await inte.response.send_message(embed=emebed_trade, view=TradeAcceptView(inte, inte.guild.id, trade_usr1, inte.user.id, trade_usr2, user.id, emebed_trade))

    
@tree.command(name="testroll", description="test")
async def tr(inte : discord.Interaction):
    r=p.roll(inte.user.id, test=True)
    await inte.response.send_message(embed=r if r else fbot.embed_wait(), ephemeral=r==None)


@tree.command(name="testdb", description="test")
async def tdb(inte : discord.Interaction):
    await inte.response.send_message(p.affiche(), ephemeral=True)


@tree.command(name="search", description="Search")
async def se(inte : discord.Interaction, name : str):
    list_search=Cards.search(name)
    await inte.response.send_message(embed=Cards.get_embed_card(list_search[0]).set_footer(text=f"1/{len(list_search)}"), ephemeral=True, view=CollectionView(Cards.search(name)))


@tree.command(name="sell", description="sell")
async def sell(inte : discord.Interaction, offre : str):
    formated_list=Cards.format_list_card(offre, p.get_player_data(inte.guild.id, inte.user.id).get("cards",{}))

    embed=discord.Embed(title="Vente")

    value=0

    for id_card, quantity in formated_list:
        rarity=Cards.get_rarity(int(id_card)).get("id")

        value+=fbot.cost_per_rarity.get(rarity, 0)*int(quantity)
    
    embed.add_field(name=f"Voulez vous vendre pour {value} gold{'s' if value>1 else ''}:", value=Cards.formated_to_str(formated_list), inline=False)

        # await inte.channel.send(f"J'ai vendu {quantity} {Cards.get_name(int(id_card))} pour {value} gold")
    await inte.response.send_message(embed=embed, view=SellView(inte, inte.guild.id, inte.user.id, formated_list, value, embed))


@tree.command(name="info_player", description="Affiche le profil du joueur")
async def info_player(inte : discord.Interaction, user : discord.User = None, show : bool = True):
    """
    TODO : verifier que la couleur existe
    """

    if user==None: user=inte.user

    data=p.get_player_data(inte.guild.id, user.id)

    try:
        color=discord.Color.from_str(data.get("color","#000000"))
    except:
        color=discord.Color.from_str("#000000")

    embed=discord.Embed(title=f"{user.global_name} ({user.name})", color=color)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Level", value=f"{data.get("level",0)}", inline=True)
    embed.add_field(name="Gold", value=f"{data.get("money",0)}", inline=True)


    await inte.response.send_message(embed=embed, ephemeral=not show)


@tree.command(name="change_color", description="Change la couleur du profil du joueur")
async def change_color(inte : discord.Interaction, color : str):
    p.set_player_color(inte.guild.id, inte.user.id, color)
    await inte.response.send_message(f"Couleur changee en {color}", ephemeral=True)


bot.run(fbot.DISCORD_TOKEN)