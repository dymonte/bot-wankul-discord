import random, requests, json, time, discord


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


maxLvl=5

with open("config.json", "r") as f:
    config = json.load(f)

DISCORD_TOKEN = config["DISCORD_TOKEN"]

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

    embed=discord.Embed(
        title="**Actions**",
        color=discord.Color.dark_gold(),
    )

    if lang=="fr":
        embed.add_field(name="/roll", value="Lancer le roll d'une carte, utilise en priorité les rolls temporaires puis les rolls en stock.", inline=False)
        embed.add_field(name="/trade", value="Entrez la personne avec qui vous voulez trade, puis les cartes proposées et celles demandées avec des *motifs*.", inline=False)
        embed.add_field(name="/shop", value="Voir le shop pour acheter des niveaux ou du stock de cartes. Les cartes stockées ne sont pas réinitialisées chaque heure.", inline=False)
        embed.add_field(name="/sell", value="Vendre des cartes selon un motif.", inline=False)

        embed.add_field(name="/auto_sell", value="Vendre automatiquement les cartes en définissant les raretés des cartes à vendre ainsi que le fait de garder ou non un exeplaire de chaque carte.\nGarder les arguments vides permet de vendre tous les doublons peu commun et inférieur", inline=False)
    embeds.append(embed)

    embed=discord.Embed(
        title="**Informations**",
        color=discord.Color.dark_gold(),
    )

    if lang=="fr":
        embed.add_field(name="/info", value="Voir les informations d'une carte en fonction de son identifiant.", inline=False)
        embed.add_field(name="/search", value="Rechercher les cartes en fonction de leur nom.", inline=False)
        embed.add_field(name="/info_player", value="Affiche les informations d'un joueur (niveau, gold)", inline=False)
        embed.add_field(name="/collection", value="Voir la collection de cartes d'un joueur (par défaut le joueur qui lance la commande)", inline=False)
        embed.add_field(name="/change_color", value="Changer la couleur du profil du joueur. (Format hexadecimal `#RRGGBB` attendu)", inline=False)
        embed.add_field(name="/help", value="Voir cette aide", inline=False)
        


    embeds.append(embed)

    if lang=="fr":
        embed=discord.Embed(
            title="**Motifs**",
            color=discord.Color.dark_gold(),
            description="Les Motifs permettent de définir une liste de cartes. Par exemple, `420|1&32|2` correspond à une fois la carte numéro 420 et deux fois la carte numéro 32, laissez simplement `&` pour un motif vide."
        )

    embeds.append(embed)

    return embeds


def format_str_search(name : str) -> str:
    return name.lower().replace("é","e").replace("à","a")



if __name__ == "__main__":
    print(formated_date())
