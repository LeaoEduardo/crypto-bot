import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

from binance import Client
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

BINANCE_API = os.environ.get('BINANCE_API', None)
BINANCE_SECRET = os.environ.get('BINANCE_SECRET', None)

def get_crypto_info(client: Client, coin_name: str, symbols: dict, interval: str, start_date: dt):
  columns = [
    "open_time",
    "open_price",
  ]

  convert_timestamp_column = lambda x: dt.fromtimestamp(x/1000)

  ticker = f'{coin_name.upper()}USDT'
  if ticker not in symbols:
    return None
  else:
    timestamp = int(start_date.timestamp()*1000)
    bars = client.get_historical_klines(ticker, interval, timestamp)
    if bars:
      hist = pd.DataFrame.from_records([dict(zip(columns, bar[:2])) for bar in bars])
      hist.open_time = hist.open_time.apply(convert_timestamp_column)
      hist.rename(columns={"open_price":coin_name.upper()}, inplace=True) 
      return hist.set_index("open_time")
    return None

def extract_latest_info(
  test: bool = False,
  coins: list = [],
  timespan: int = 1,
  interval: str = '1h',
):
  
  print(f"test:{test}, timespan:{timespan}, interval:{interval}")

  if not coins:
    raise ValueError("coins can't be None")

  start_datetime = dt.now()-relativedelta(days=timespan)
  start_date = dt(start_datetime.year, start_datetime.month, start_datetime.day)

  client = Client(BINANCE_API, BINANCE_SECRET)
  if test:
    client.API_URL = 'https://testnet.binance.vision/api'

  exchange_info = pd.DataFrame.from_records(client.get_exchange_info()['symbols'])
  
  dfs = []
  for coin in coins:
    crypto_info = get_crypto_info(client, coin, exchange_info.symbol.values, interval=interval, start_date=start_date)
    if crypto_info is not None:
      dfs.append(crypto_info)

  return pd.concat(dfs, axis=1)

@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your transformation logic here
    params = {
        k:eval(v) if k != 'interval' and isinstance(v, str) else v
        for k,v in kwargs.items() 
        if k in ('test', 'timespan', 'interval')
        }
    params['coins'] = data

    return extract_latest_info(**params).dropna(axis=1)

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
