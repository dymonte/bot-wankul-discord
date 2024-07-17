import requests, json, discord, random

with open("config.json", "r") as f:
    url = json.load(f).get("API_URL", "http://localhost:3000")




class Cards():

    def get_all_cards():
        return requests.request("GET",url+"/v1/card").json()
    
    def get_cards_by_rarity(rarity):
        return requests.request("GET",url+f"/v1/rarity/{rarity}/list").json()
    
    def get_rarities():
        return requests.request("GET",url+"/v1/rarity").json()

    def get_card(id_card):
        return requests.request("GET",url+"/v1/card/"+str(id_card)).json()
    
    def get_rarity(id_card):
        return requests.request("GET",url+"/v1/card/"+str(id_card)+"/rarity").json()
    
    def get_name(id_card):
        return requests.request("GET",url+"/v1/card/"+str(id_card)+"/name").json()

    def get_embed_card(id_card : int, quantity : int = 0, detailed : bool = False)->discord.Embed:
        card=Cards.get_card(id_card)

        if detailed:
            embed = discord.Embed(
                title=f"{card.get('title','-')} "+(""if quantity==0 else f" *({quantity}x)*"),
                description=f"**#{id_card}**\n{card.get('rarity', {}).get('name','')}\n{card.get('description','')}\n",
                color=discord.Colour.from_str(card.get("season", {}).get("color", "#000000")),
            )


            if card.get("rarityId")==1:
                embed.add_field(name="Effet victoire", value=f"{card.get('tWinningEffect','')}", inline=False)
                embed.add_field(name="Effet défaite", value=f"{card.get('tLosingEffect','')}", inline=False)
                embed.add_field(name="Effet sp\u00ecial", value=f"{card.get('tSpecialEffect','')}", inline=False)
            

            embed.set_thumbnail(url=card["image"])

            embed.set_footer(text=f"Par {card.get('artist',{}).get('name','')}")
        else:
            embed = discord.Embed(
                title=f"{card.get('title','-')} "+(""if quantity==0 else f" *({quantity}x)*"),
                description=f"**#{id_card}**\n{card.get("rarity", {}).get('accronym','')}",
                color=discord.Colour.from_str(card.get("season", {}).get("color", "#000000")),
            )

            embed.set_image(url=card["image"])

        return embed
    


    def random_card():
        rarities=Cards.get_rarities()[:9] # ne garde que jusqu'a la rarete gold

        rarity=random.choices(rarities, [float(i.get("txDrop",0).replace("%","")) for i in rarities], k=1)[0]

        card=random.choice(Cards.get_cards_by_rarity(rarity["id"]))
        return card

    

    def search(name : str)->list:
        cards= Cards.get_all_cards()

        return [card["id"] for card in cards if name.lower().replace("é","e").replace("à","a") in card["name"].lower().replace("é","e").replace("à","a")]
    


    def format_list_card(l : str, cards : dict)-> list:# exemple [[122,2],[384,1]] sans prendre en compte les cartes non possédées ou en trop faible quantité
        """
        l : la liste des cartes sous forme 122|2&384|1
        cards : le dictionnaire des cartes possédées par le joueur
        """

        print(cards)

        all_cards=[[int(e) for e in i.split("|") if e!=""] for i in l.split("&") if i!=""] # mise sous forme de liste de la chaine de caractere
        return [e for e in all_cards if cards.get(str(e[0]),0)>=e[1] or e==''] # ne garde que les cartes possedees en assez grande quantite
    


    def formated_to_str(l : list)->str:
        res=""
        for e in l:
            res+=f"{Cards.get_name(e[0])}({Cards.get_rarity(e[0]).get('accronym','')})x{e[1]}  "
        return res














if __name__ == "__main__":
    for i in range(100):
        print(i, Cards.random_card()["rarity"]["name"]) #Cards.random_card()

    print('\u00e9')
    # # print((0,1)==[0,1])
    # pass