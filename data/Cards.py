import requests, json, discord, random

with open("config.json", "r") as f:
    url = json.load(f).get("API_URL", "http://localhost:3000")




class Cards():

    def get_all_cards():
        return requests.request("GET",url+"/v1/card").json()
    
    def get_cards_by_rarity(rarity):
        return requests.request("GET",url+f"/v1/rarity/{rarity}/cards").json()
    
    def get_rarities():
        return requests.request("GET",url+"/v1/rarity").json()

    def get_card(id_card):
        return requests.request("GET",url+"/v1/card/"+str(id_card)).json()
    

    def get_embed_card(id_card : int, quantity : int = 0, detailed : bool = False)->discord.Embed:
        card=Cards.get_card(id_card)

        if detailed:
            embed = discord.Embed(
                title=f"{card.get('title','-')} "+(""if quantity==0 else f" *({quantity}x)*"),
                description=f"**#{id_card}**\n{card.get('rarity', {}).get('name','')}\n{card.get('description','')}\n",
                color=discord.Colour.from_str(card.get("season", {}).get("color", "#000000")),
            )

            embed.set_thumbnail(url=card["image"])
        else:
            embed = discord.Embed(
                title=f"{card.get('title','-')} "+(""if quantity==0 else f" *({quantity}x)*"),
                description=f"**#{id_card}**\n{card.get("rarity", {}).get('accronym','')}",
                color=discord.Colour.from_str(card.get("season", {}).get("color", "#000000")),
            )

            embed.set_image(url=card["image"])

        return embed
    

    # def random_card():
    #     resp=Cards.get_all_cards()

    #     return random.choices(resp, [0.1 if e["drop"]=="N/A" or e["drop"]=="" else float(e["drop"].replace("%","").replace(" des boosters","")) for e in resp], k=1)[0]
    
    def random_card():

        rarities=Cards.get_rarities()[:9]

        # print( [float(i.get("txDrop",0).replace("%","")) for i in rarities])

        rarity=random.choices(rarities, [float(i.get("txDrop",0).replace("%","")) for i in rarities], k=1)[0]
        
        a=0
        # while rarity["id"]!=9:
        #     rarity=random.choices(rarities, [float(i.get("txDrop",0).replace("%","")) for i in rarities], k=1)[0]
        #     print(rarity["name"])
        #     a+=1
        # print(a)

        card=random.choice(Cards.get_cards_by_rarity(rarity["id"]))
        return card
        # print(f"{rarity['name']} : {card['title']}")
        # print(Cards.get_cards_by_rarity(rarities))



    def get_name_card(id_card):
        return Cards.get_card(id_card).get("title")
    

    def search(name : str)->list:
        cards= Cards.get_all_cards()

        return [card["id"] for card in cards if name.lower().replace("é","e").replace("à","a") in card["name"].lower().replace("é","e").replace("à","a")]
    

if __name__ == "__main__":
    # for i in range(100):Cards.random_card()
    # print((0,1)==[0,1])
    pass