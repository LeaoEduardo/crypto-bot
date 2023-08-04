import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

from binance import Client
import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

BINANCE_API = os.environ.get('BINANCE_API', None)
BINANCE_SECRET = os.environ.get('BINANCE_SECRET', None)

def get_crypto_info(client: Client, coin_name: str, exchange_info: dict, interval: str, start_date: dt):
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

def extract_latest_info(
  test: bool = False,
  coins: list = [],
  timespan: int = 1,
  interval: str = '1h',
):
  
  print(f"test:{test}, timespan:{timespan}, interval:{interval}")

  start_datetime = dt.now()-relativedelta(days=timespan)
  start_date = dt(start_datetime.year, start_datetime.month, start_datetime.day)

  client = Client(BINANCE_API, BINANCE_SECRET)
  if test:
    client.API_URL = 'https://testnet.binance.vision/api'

  exchange_info = pd.DataFrame.from_records(client.get_exchange_info()['symbols'])
  if not coins:
    coins = exchange_info.baseAsset.unique()

  dfs = []
  for coin in coins:
    crypto_info = get_crypto_info(client, coin, exchange_info, interval=interval, start_date=start_date)
    if crypto_info is not None:
      dfs.append(crypto_info)

  return pd.concat(dfs, ignore_index=True)


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Load data from API
    """
    params = {
        k:eval(v) if k != 'interval' and isinstance(v, str) else v
        for k,v in kwargs.items() 
        if k in ('test', 'coins', 'timespan', 'interval')
        }
    return extract_latest_info(**params)

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
