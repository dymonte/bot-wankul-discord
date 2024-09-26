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




def formated_date()->list:
    return [time.localtime().tm_year,time.localtime().tm_yday,time.localtime().tm_hour]


embed_error = discord.Embed(
    title="Error",
    description="You can't roll yet !",
    color=discord.Color.red(),
)

def embed_wait() -> discord.Embed:
    return discord.Embed(
        title="Pas de roll restants",
        description=f"Attendez {60-time.localtime().tm_min} min avant de pouvoir roll ou achetez-en dans le `/shop`.",
        color=discord.Color.dark_gold(),
    )

def embed_shop(level : int, stock : int, money : int) -> discord.Embed:
    embed=discord.Embed(
        title=f"**Shop** - 🪙 {money}",
        color=discord.Color.dark_gold(),
    )
    embed.add_field(name=f"💎 **Level Up** (🪙{"-" if level>=5 else shop_prices['lvlUp'][level+1]})", value=f"Augmentez votre niveau\nVous êtes actuellement niveau {level}/5", inline=False)

    embed.add_field(name="🃏 **Acheter 3 cartes** (🪙30)", value=f"Achetez des stocks de roll supplémentaires\nVous avez actuellement {stock} en stock", inline=False)

    return embed



def embed_help(lang : str="fr") -> list[discord.Embed]:
    
    embeds=[]

    embed=discord.Embed(
        title="**Introduction**",
        color=discord.Color.dark_gold(),
        description=f"Ce bot permet de roll et de collectionner des cartes du jeu Wankul. Pour commencer, utilisez `/roll`.\n\
            Par défaut, vous possédez {default_nb_rolls} rolls par heure, ce qui peut être amélioré dans la boutique."
    )

    embeds.append(embed)
    
    
    with open("help.json") as f:
        help_dict=json.load(f)
    
    for i in help_dict:
        embed=discord.Embed(
            title=i["name"],
            color=discord.Color.dark_gold(),
        )
        for j in i["fields"]:
            embed.add_field(name=j["command"], value=j["description"], inline=False)
        
        embeds.append(embed)



    if lang=="fr":
        embed=discord.Embed(
            title="**Motifs**",
            color=discord.Color.dark_gold(),
            description="Les Motifs permettent de définir une liste de cartes. Par exemple, `420|1&32|2` correspond à une fois la carte numéro 420 et deux fois la carte numéro 32, laissez simplement `&` pour un motif vide. Ajoutez un espace, une valeur puis \"g\" pour inclure de l'argent (uniquement pour les échanges)."
        )

    embeds.append(embed)

    return embeds


def format_str_search(name : str) -> str:
    return name.lower().replace("é","e").replace("à","a").replace(" ","")



if __name__ == "__main__":
    print(formated_date())
    print(API_URL)
