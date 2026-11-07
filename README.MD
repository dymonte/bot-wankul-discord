sudo systemctl start mongod


# Projet Wankul Bot

Ce projet est un bot Discord développé en Python qui permet aux utilisateurs de jouer à un jeu de cartes appelé [Wankul](https://wankul.com).

## Fonctionnalités

* Obtenir et collectionner des cartes
* Echanger des cartes avec d'autres joueurs
* Vendre des cartes pour obtenir de l'or
* Acheter des cartes dans un magasin et améliorer son niveau dans la boutique

## Installation

Pour installer le bot, vous devez avoir Python et les dépendances suivantes :

* discord.py
* pymongo

Vous pouvez installer les dépendances en exécutant la commande suivante :

```bash
pip install discord.py pymongo
```

Il est également nécessaire d'avoir mongodb installé.

## Configuration
Vous devez configurer le bot en créant un fichier `.env` avec les variables suivantes :

- `DISCORD_TOKEN` : le token de votre bot Discord
- `API_URL` : l'URL de l'[API](https://github.com/dymonte/api-wankul) que le bot utilise
- `DB_HOST` : l'URL de la base de données Mongo 
- `DB_PORT` : le port de la base de données

Pour lancer le bot, exécutez la commande suivante :
```bash
python3 bot.py
```
# Commandes
Voici les commandes principales que le bot supporte :

- `/roll` : obtenir une carte
- `/trade` : échanger des cartes avec d'autres joueurs
- `/shop` : acheter des cartes dans un magasin
- `/sell` : vendre des cartes pour obtenir de l'or
- `/help` : afficher l'aide

Utilisez `/help` pour voir toutes les commandes disponibles
