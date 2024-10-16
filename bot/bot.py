# --- Imports discord ---
import discord
from discord.ext import commands
from discord import app_commands


# --- Imports extern ---


# --- Imports intern ---
import database.PlayerDB as PlayerDB
import fbot
from database.Player import Player
from Views.Collection import CollectionView
from Views.Trade import TradeAcceptView
from Views.Sell import SellView
from Views.Shop import ShopView
from data.Cards import Cards




p=PlayerDB.PlayerDatabase() # p -> base de donnee des joueurs

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


# --- Test ---
@tree.command(name="drop", description="drop")
async def dr(inte : discord.Interaction):
    """
    TODO
    """
    p.drop_table(inte.guild.id)
    await inte.response.send_message("done", ephemeral=True)

@tree.command(name="testdb", description="test")
async def tdb(inte : discord.Interaction):
    await inte.response.send_message(p.debug_affiche(), ephemeral=True)



# --- Cards ---
@tree.command(name="roll", description="roll")
async def roll(inte : discord.Interaction):
    player=Player(inte.guild.id, inte.user.id)
    r=await player.roll()
    await inte.response.send_message(embed=r if r else fbot.embed_wait(), ephemeral=r==None, delete_after=(7 if r==None else None))


@tree.command(name="collection", description="list")
async def cl(inte : discord.Interaction, user : discord.User = None, show : bool = True):
    id_user = user.id if user!=None else inte.user.id
    player=Player(inte.guild.id, id_user)
    list_of_cards=player.list_of_cards()

    if len(list_of_cards)==0:
        await inte.response.send_message(content="aucune carte", ephemeral=True)
    elif len(list_of_cards)==1:
        await inte.response.send_message(ephemeral=not show, embed=(await Cards.get_embed_card(list_of_cards[0][0], list_of_cards[0][1])).set_footer(text="1/1"))
    else:
        await inte.response.send_message(ephemeral=not show, embed=(await Cards.get_embed_card(list_of_cards[0][0], list_of_cards[0][1])).set_footer(text=f"1/{len(list_of_cards)}"), view=CollectionView(list_of_cards))


@tree.command(name="info_card", description="Informations sur une carte")
async def cl(inte : discord.Interaction, id_card : int, show : bool = True):
    # id_user = user.id if user!=None else inte.user.id
    player=Player(inte.guild.id, inte.user.id)

    emb=await Cards.get_embed_card(id_card,quantity=player.data.get("cards",{}).get(str(id_card),0) ,detailed=True)

    await inte.response.send_message(embed=emb if emb != None else discord.Embed(title="Carte introuvable", color=discord.Color.red()), ephemeral=not show or emb==None, delete_after=(5 if emb==None else None))


@tree.command(name="trade", description="exemple de format de trade : \"125|1&18|2 10g\" ('&' correspond a vide)")
async def te(inte : discord.Interaction, user : discord.User, offre : str, demande : str):
    """
    TODO : gerer les cas de motifs invalides
    """
    player1=Player(inte.guild.id, inte.user.id)
    player2=Player(inte.guild.id, user.id)

    trade_usr1,money_usr1=Cards.format_list_card(offre, player1.data.get("cards",{}), player1.get("gold"))
    trade_usr2,money_usr2=Cards.format_list_card(demande, player2.data.get("cards",{}), player2.get("gold"))

    emebed_trade=discord.Embed(title="Trade")

    format1=await Cards.formated_to_str(trade_usr1)
    format2=await Cards.formated_to_str(trade_usr2)
    emebed_trade.add_field(name=f"En attente de {inte.user.name}", value=f"{format1 if format1!="" else "(vide)"} + {money_usr1} 🪙", inline=False)
    emebed_trade.add_field(name=f"En attente de {user.name}", value=f"{format2 if format2!="" else "(vide)"} + {money_usr2} 🪙", inline=False)

    await inte.response.send_message(embed=emebed_trade, view=TradeAcceptView(inte, inte.guild.id, trade_usr1, money_usr1, player1, trade_usr2, money_usr2, player2, emebed_trade))


@tree.command(name="search", description="Search")
async def se(inte : discord.Interaction, name : str):
    list_search=await Cards.search(name)
    if len(list_search)==0:
        await inte.response.send_message(embed=discord.Embed(title="Aucun résultat", color=discord.Color.red()), ephemeral=True, delete_after=5)
    elif len(list_search)==1:
        await inte.response.send_message(ephemeral=True, embed=(await Cards.get_embed_card(list_search[0])).set_footer(text="1/1"))
    else:
        await inte.response.send_message(embed=(await Cards.get_embed_card(list_search[0])).set_footer(text=f"1/{len(list_search)}"), ephemeral=True, view=CollectionView(list_search))


@tree.command(name="sell", description="sell")
async def sell(inte : discord.Interaction, offre : str):
    player=Player(inte.guild.id, inte.user.id)

    formated_list=Cards.format_list_card(offre, player.data.get("cards",{}))[0]
    

    value=0

    for id_card, quantity in formated_list:
        rarity=(await Cards.get_rarity(int(id_card))).get("id")

        value+=fbot.cost_per_rarity.get(rarity, 0)*int(quantity)
    
    await send_sell_message(inte, player, formated_list, value)


@tree.command(name="auto_sell", description="vendre automatiquement (max 30 cartes)")
async def auto_sell(inte : discord.Interaction, rarity : int = 3, keep_one : bool = True):
    player=Player(inte.guild.id, inte.user.id)
    cards=player.data.get("cards",{})

    quantity_to_keep=(1 if keep_one else 0)

    total_price=0


    formated_list=[]

    for id_card, quantity in cards.items():
        if len(formated_list)>=30:
            break
        card_rarity=(await Cards.get_rarity(int(id_card))).get("id")
        if quantity>quantity_to_keep and card_rarity <=rarity:
            quantity_to_sell=quantity-quantity_to_keep
            formated_list.append((id_card, quantity_to_sell))

            total_price+=fbot.cost_per_rarity.get((await Cards.get_rarity(int(id_card))).get("id"), 0)*(quantity_to_sell)

    if len(formated_list)>0: await send_sell_message(inte, player, formated_list, total_price)
    else : await inte.response.send_message(content="aucune carte", ephemeral=True, delete_after=5)


async def send_sell_message(inte : discord.Interaction, player : Player, formated_list : list, value : int) -> None:
    """
    Envoie l'embed de vente
    """
    embed=discord.Embed(title="Vente")

    embed.add_field(name=f"Voulez vous vendre pour {value} gold{'s' if value>1 else ''}:", value=await Cards.formated_to_str(formated_list), inline=False)

    await inte.response.send_message(embed=embed, view=SellView(inte, player, formated_list, value, embed), ephemeral=True)



# --- Player ---
@tree.command(name="info_player", description="Affiche le profil du joueur")
async def info_player(inte : discord.Interaction, user : discord.User = None, show : bool = True):
    if user==None: user=inte.user

    player=Player(inte.guild.id, user.id)

    try:
        color=discord.Color.from_str(player.get("color"))
    except:
        color=discord.Color.from_str("#000000")

    embed=discord.Embed(title=f"{user.global_name} ({user.name})", color=color)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="💎 Level", value=f"{player.get("level")}", inline=True)
    embed.add_field(name="🪙 Gold", value=f"{player.get("gold")}", inline=True)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="📦 Stock", value=f"{player.get("stock")}", inline=True)
    embed.add_field(name="✨ Wish", value=f"{player.get("wish")}", inline=True)

    await inte.response.send_message(embed=embed, ephemeral=not show)


@tree.command(name="change_color", description="Change la couleur du profil du joueur")
async def change_color(inte : discord.Interaction, color : str):
    
    Player(inte.guild.id, inte.user.id).set("color",color)
    if "#" not in color: color=f"#{color}" #discord n'autorise qu'avec # au debut
    await inte.response.send_message(f"Couleur changee en {color}", ephemeral=True)


@tree.command(name="shop", description="Ouvrir le shop")
async def shop(inte : discord.Interaction):
    player=Player(inte.guild.id, inte.user.id)
    embed=fbot.embed_shop(player.get("level"), player.get("stock"), player.get("gold"))
    
    await inte.response.send_message(embed=embed, ephemeral=True, view=ShopView(inte, player, embed))

@tree.command(name="wish", description="Définit un nouveau wish ou affiche l'actuel")
async def wish(inte : discord.Interaction, w : int = 0):
    player=Player(inte.guild.id, inte.user.id)
    if w==0:
        await inte.response.send_message(f"Votre wish actuel est {player.get("wish")}")
    else:
        player.set("wish", w)
        await inte.response.send_message(f"Votre wish est maintenant {w}")


# --- Help ---
@tree.command(name="help", description="Aide")
@app_commands.choices(command=fbot.help_choices)
async def help(inte : discord.Interaction, command : discord.app_commands.Choice[str] = None):
    if command!=None: command=command.value
    embeds=fbot.embed_help(command)
    await inte.response.send_message(embeds=embeds, ephemeral=True, delete_after=120)

@tree.command(name="feedback", description="Permet d'afficher le formulaire de Feedback")
async def feedback(inte : discord.Interaction):
    await inte.response.send_message(content=f"Feedback : https://forms.gle/PoMnBvC8JVQ2WofAA", ephemeral=True, delete_after=120)
    

@tree.command(name="discord", description="Permet d'afficher le lien du discord officiel du bot")
async def disc(inte : discord.Interaction):
    await inte.response.send_message(content="https://discord.gg/", ephemeral=True, delete_after=120)






# --- Run ---
bot.run(fbot.DISCORD_TOKEN)
