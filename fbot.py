import random, requests, json, time, discord


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
    "lvlUp":1000,
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
        description=f"{60-time.localtime().tm_min} min avant de pouvoir roll",
        color=discord.Color.dark_gold(),
    )

def embed_shop(level : int, stock : int, money : int) -> discord.Embed:
    embed=discord.Embed(
        title=f"**Shop** - 🪙 {money}",
        color=discord.Color.dark_gold(),
    )
    if level<5: embed.add_field(name="💎 Level Up *(🪙1000)*", value=f"Augmentez votre niveau\nVous êtes actuellement niveau {level}/5", inline=False)

    embed.add_field(name="🃏 Acheter 3 cartes (🪙30)", value=f"Achetez des stocks de roll supplémentaires\nVous avez actuellement {stock} en stock", inline=False)

    return embed


if __name__ == "__main__":
    print(formated_date())
