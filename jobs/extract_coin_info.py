import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from tqdm import tqdm
from binance import Client
import pandas as pd

load_dotenv("../.env")

BINANCE_API = os.environ.get('BINANCE_API', None)
BINANCE_SECRET = os.environ.get('BINANCE_SECRET', None)

test = False
timespam = 30
coins = []

def get_crypto_info(client, coin_name, exchange_info, interval='1d', start_date=dt.now()-relativedelta(days=30)):
  columns = [
    "open_time",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume",
  ]

  convert_timestamp_column = lambda x: dt.fromtimestamp(x/1000)

  ticker = f'{coin_name.upper()}USDT'
  if ticker not in exchange_info.symbol.values:
    return None
  else:
    timestamp = int(start_date.timestamp()*1000)
    bars = client.get_historical_klines(ticker, interval, timestamp)
    if bars:
      hist = pd.DataFrame.from_records([dict(zip(columns, bar[:-1])) for bar in bars])
      hist.open_time = hist.open_time.apply(convert_timestamp_column)
      hist.close_time = hist.close_time.apply(convert_timestamp_column)
      hist["coin_name"] = coin_name.upper()
      hist["ticker"] = ticker
      return hist
    return None

def main():

  client = Client(BINANCE_API, BINANCE_SECRET)
  if test:
    client.API_URL = 'https://testnet.binance.vision/api'

  exchange_info = pd.DataFrame.from_records(client.get_exchange_info()['symbols'])
  if not coins:
    coins = exchange_info.baseAsset.unique()

  dfs = []
  for coin in tqdm(coins):
    crypto_info = get_crypto_info(client, coin, exchange_info)
    if crypto_info is not None:
      dfs.append(crypto_info)

  pd.concat(dfs, ignore_index=True).to_csv("crypto_info.csv")

if __name__ == '__main__':
  main()