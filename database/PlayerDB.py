import discord, fbot
from database.Database import Database
from data.Cards import Cards



class PlayerDatabase(Database):

    def __init__(self) -> None:
        super().__init__()
        self.players_table=self.db["players"]

        


    def drop_table(self) -> None:
        """
        Supprime la table players
        TODO : Supprimer uniquement pour le serveur en question
        """
        self.players_table.drop()


    



    def affiche(self) -> list:
        """
        Affiche et renvoie la base de donnée sour forme de liste
        """
        for i in self.players_table.find():
            print(i)
        return [i for i in self.players_table.find()]
    

