FROM python:3.11-slim

WORKDIR /bot

# Copier d'abord les fichiers de dépendances
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers du dossier bot
COPY bot/ .

# Définir PYTHONUNBUFFERED pour avoir les logs en temps réel
ENV PYTHONUNBUFFERED=1

# Lancer le bot
CMD ["python", "bot.py"]
