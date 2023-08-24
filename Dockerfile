FROM mageai/mageai

COPY crypto-bot/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN rm requirements.txt