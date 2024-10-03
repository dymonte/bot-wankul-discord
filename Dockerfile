FROM python:3.11-slim

WORKDIR /bot

COPY bot/ /bot/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python3", "bot.py"]
