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


def get_coins(
  test: bool = False,
):
  
  print(f"test:{test}")

  client = Client(BINANCE_API, BINANCE_SECRET)
  if test:
    client.API_URL = 'https://testnet.binance.vision/api'

  exchange_info = pd.DataFrame.from_records(client.get_exchange_info()['symbols'])
  coins = exchange_info.baseAsset.unique()

  return coins


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Load data from API
    """
    params = {
        k:eval(v) if k != 'interval' and isinstance(v, str) else v
        for k,v in kwargs.items() 
        if k in ('test')
        }
    return get_coins(**params)

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
