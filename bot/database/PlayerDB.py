import discord, fbot
from database.Database import Database
from data.Cards import Cards



class PlayerDatabase(Database):

    def __init__(self) -> None:
        """
        Initialise la base de données des joueurs.

        Appelle le constructeur de la classe parente, puis récupère la table "players" de la base de données.
        """
        super().__init__()
        self.players_table=self.db["players"]

    def drop_table(self,guild_id : int) -> None:
        """
        Supprime les données des joueurs d'un serveur spécifique de la base de données.

        Args:
            guild_id (int): L'ID du serveur dont les données des joueurs doivent être supprimées.

        Returns:
            None
        """
        self.players_table.delete_one({"_id":str(guild_id)})

    def debug_affiche(self) -> list:     
        """
        Récupère et affiche toutes les entrées de données des joueurs de la base de données.

        Parcourt tous les documents de la table players, affichant chacun d'eux.
        Retourne une liste contenant toutes les entrées de données des joueurs.

        Returns:
            list: Une liste de toutes les entrées de données des joueurs.
        """

        for i in self.players_table.find():
            print(i)
        return [i for i in self.players_table.find()]