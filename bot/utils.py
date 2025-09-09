# fichier contenant les variables par defaut et fonctions du bot
import json, time, discord

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = os.getenv('API_URL')



default_nb_rolls=5

cost_per_rarity={
    1:1,
    2:1,
    3:2,
    4:5,
    5:10,
    6:15,
    7:25,
    8:50,
    9:100
}

shop_prices={
    "lvlUp":{
        1:500,
        2:1000,
        3:1000,
        4:2000,
        5:5000
    },
    "stock":30
}


maxLvl=len(shop_prices["lvlUp"].keys())

with open("help.json") as f:
    help_dict=json.load(f)

help_choices=[]
for i in help_dict:
    for j in i["fields"]:
        help_choices.append(discord.app_commands.Choice(name=j["name"], value=j["name"]))


def formated_date()->list:
    """
    Returns the current date in the format [year, day of the year, hour]

    Returns:
        list: a list containing the current year, day of the year and hour
    """
    return [time.localtime().tm_year,time.localtime().tm_yday,time.localtime().tm_hour]


embed_error = discord.Embed(
    title="Error",
    description="You can't roll yet !",
    color=discord.Color.red(),
)

def embed_wait() -> discord.Embed:
    """
    Returns an embed that says that the user has no more rolls left
    
    Returns:
        discord.Embed: the embed
    """
    return discord.Embed(
        title="Pas de roll restants",
        description=f"Attendez {60-time.localtime().tm_min} min avant de pouvoir roll ou achetez-en dans le `/shop`.",
        color=discord.Color.dark_gold(),
    )

def embed_shop(level : int, stock : int, money : int) -> discord.Embed:
    """
    Returns an embed for the shop
    
    Parameters:
        level (int): the player's level
        stock (int): the player's current stock
        money (int): the player's current gold
    
    Returns:
        discord.Embed: the embed
    """
    embed=discord.Embed(
        title=f"**Shop** - 🪙 {money}",
        color=discord.Color.dark_gold(),
    )
    embed.add_field(name=f"💎 **Level Up** (🪙 {"-" if level>=5 else shop_prices['lvlUp'][level+1]})", value=f"Augmentez votre niveau\nVous êtes actuellement niveau {level}/5", inline=False)

    embed.add_field(name="🃏 **Acheter 3 cartes** (🪙 30)", value=f"Achetez des stocks de roll supplémentaires\nVous avez actuellement {stock} en stock", inline=False)

    return embed



def embed_help(command : str=None, lang : str="fr") -> list[discord.Embed]:
    
    """
    Returns an embed or a list of embeds for the help command.
    
    Parameters:
        command (str): the command to display the help for, if None, displays the introduction and all commands.
        lang (str): the language to display the help in, currently only "fr" is supported.
    
    Returns:
        list[discord.Embed]: a list of embeds for the help command, or None if the command is not found.
    """
    embeds=[]       
        
        
    if lang=="fr":
        embed_motif=discord.Embed(
            title="**Motifs**",
            color=discord.Color.dark_gold(),
            description="Les Motifs permettent de définir une liste de cartes." \
            "Pour cela, vous devez écrire des couples contenant un numéro de carte et une quantité séparés par un `|`. Chaque couple est séparé par un `&`." \
            "Ajoutez un espace, une valeur puis `g` pour inclure de l'argent (uniquement pour les échanges)." \
            "Exemple: `420|1&32|2 10g` correspond à une fois la carte numéro 420 et deux fois la carte numéro 32 et 10 gold, laissez simplement `&` pour un motif vide."
        )


    if command!=None:
        for i in help_dict:
            for j in i["fields"]:
                if format_str_search(command) in format_str_search(j["name"]):
                    embeds=[discord.Embed(
                        title=f"`{j['command']}`",
                        color=discord.Color.dark_gold(),
                        description=j["description"]
                    )]
                    if j["hasMotif"]:embeds.append(embed_motif)
                    return embeds
        return None

    else:
    
        embed=discord.Embed(
            title="**Introduction**",
            color=discord.Color.dark_gold(),
            description=f"Ce bot permet de roll et de collectionner des cartes du jeu Wankul. Pour commencer, utilisez `/roll`.\n\
                Par défaut, vous possédez {default_nb_rolls} rolls par heure, ce qui peut être amélioré dans la boutique."
        )

        embeds.append(embed)

        
        for i in help_dict:
            embed=discord.Embed(
                title=i["name"],
                color=discord.Color.dark_gold(),
                description=""
            )
            for j in i["fields"]:
                embed.description+=f"`{j['command']}`, "
            
            embeds.append(embed)
        
        embeds.append(embed_motif)

        return embeds


def format_str_search(name : str) -> str:
    """
    Formats a string for search by converting it to lowercase and replacing certain accented characters and spaces.

    Parameters:
        name (str): The input string to be formatted.

    Returns:
        str: The formatted string with lowercase characters and specific replacements.
    """

    return name.lower().replace("é","e").replace("à","a").replace(" ","")

def get_emoji_for_rarity(rarity : int) -> str:
    """
    Returns the emoji for the given rarity.

    Parameters:
        rarity (int): The rarity of the card.

    Returns:
        str: The emoji for the given rarity.
    """
    match rarity:
        case 5 | 6:
            return "✨"
        case 7:
            return "🥉"
        case 8:
            return "🥈"
        case 9:
            return "🥇"
        case _:
            return ""



if __name__ == "__main__":
    print(embed_help("help")[0])