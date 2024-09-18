import json, discord, random

import fbot

import aiohttp

with open("config.json", "r") as f:
    url = json.load(f).get("API_URL", "http://localhost:3000")




class Cards():

    async def get_all_cards():
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/v1/card/list") as resp:
                return await resp.json()

    async def get_cards_by_rarity(rarity):
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/v1/rarity/"+str(rarity)+"/list") as resp:
                return await resp.json()
    
    async def get_rarities():
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/v1/rarity") as resp:
                return await resp.json()

    async def get_card(id_card):
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/v1/card/"+str(id_card)) as resp:
                return await resp.json()

    
    async def get_rarity(id_card):
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/v1/card/"+str(id_card)+"/rarity") as resp:
                return await resp.json()

    async def get_name(id_card):
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/v1/card/"+str(id_card)+"/name") as resp:
                return await resp.json()

    async def get_embed_card(id_card : int, quantity : int = 0, detailed : bool = False)->discord.Embed:
        card=await Cards.get_card(id_card)

        if detailed:
            embed = discord.Embed(
                title=f"**{card.get('title','-')}** "+(""if quantity==0 else f" *({quantity}x)*"),
                description=f"**#{id_card}**\n{card.get('rarity', {}).get('name','')}\n{card.get('description','')}\n",
                color=discord.Colour.from_str(card.get("season", {}).get("color", "#000000")),
            )


            if card.get("rarityId",1)==1:
                embed.add_field(name="Effet victoire", value=f"{card.get('tWinningEffect','')}", inline=False)
                embed.add_field(name="Effet défaite", value=f"{card.get('tLosingEffect','')}", inline=False)
                embed.add_field(name="Effet sp\u00e9cial", value=f"{card.get('tSpecialEffect','')}", inline=False)
            
            else:
                embed.add_field(name="Règle", value=f"{card.get('rules','')}", inline=False)
                if card.get("combo"): embed.add_field(name="Combo", value=f"{card.get('combo','')}", inline=False)
                embed.add_field(name="Quote", value=f"{card.get('quote','')}", inline=False)

            embed.set_thumbnail(url=card["image"])

            embed.set_footer(text=f"Par {card.get('artist',{}).get('name','')}")

        else:
            embed = discord.Embed(
                title=f"**{card.get('title','-')}** "+(""if quantity==0 else f" *({quantity}x)*"),
                description=f"**#{id_card}**\n{card.get("rarity", {}).get('accronym','')}",
                color=discord.Colour.from_str(card.get("season", {}).get("color", "#000000")),
            )

            embed.set_image(url=card["image"])

        return embed
    

    async def random_card():
        rarities=await Cards.get_rarities()
        rarities=rarities[:9] # ne garde que jusqu'a la rarete gold

        rarity=random.choices(rarities, [float(i.get("txDrop",0).replace("%","")) for i in rarities], k=1)[0]

        card=random.choice(await Cards.get_cards_by_rarity(rarity["id"]))
        return card

    

    async def search(name : str)->list:
        cards=await Cards.get_all_cards()

        return [card["id"] for card in cards if fbot.format_str_search(name) in fbot.format_str_search(card["name"])]
    


    def format_list_card(l : str, cards : dict)-> list:# exemple [[122,2],[384,1]] sans prendre en compte les cartes non possédées ou en trop faible quantité
        """
        l : la liste des cartes sous forme 122|2&384|1
        cards : le dictionnaire des cartes possédées par le joueur
        """

        print(cards)

        all_cards=[[int(e) for e in i.split("|") if e!=""] for i in l.split("&") if i!=""] # mise sous forme de liste de la chaine de caractere
        return [e for e in all_cards if cards.get(str(e[0]),0)>=e[1] or e==''] # ne garde que les cartes possedees en assez grande quantite
    


    async def formated_to_str(l : list)->str:
        """
        l : la liste des cartes sous forme [[122,2],[384,1]]
        retourne sous la forme d'une str: "name(raity)xquantity  name(raity)xquantity"
        """
        res=""
        for e in l:
            res+=f"{await Cards.get_name(e[0])}({(await Cards.get_rarity(e[0])).get('accronym','')})x{e[1]}  "
        return res



if __name__ == "__main__":
    for i in range(100):
        print(i, Cards.random_card()["rarity"]["name"]) #Cards.random_card()
