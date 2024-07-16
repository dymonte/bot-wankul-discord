import random, requests, json, time, discord



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

def format_list_card(l : str, cards : dict)-> list:# exemple [[122,2],[384,1]] sans prendre en compte les cartes non possédées ou en trop faible quantité
    all_cards=[[int(e) for e in i.split("|") if e!=""] for i in l.split("&") if i!=""]
    return [e for e in all_cards if cards.get(str(e[0]),0)>=e[1] or e=='']


if __name__ == "__main__":
    print(formated_date())
