FROM python:alpine3.20

WORKDIR /bot

COPY bot/ /bot/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python3", "bot.py"]
