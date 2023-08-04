import pandas as pd
import sys
sys.path.append('crypto-bot')

from utils.cg_api import CoinGeckoAPI

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    cg_api = CoinGeckoAPI()
    all_coins = cg_api.get_all_coins()

    print("Columns: ", all_coins.columns)

    if 'symbol' not in all_coins.columns:
        raise Exception('API rate exceeded')

    symbols = list(all_coins.symbol.values)

    return {"symbols": symbols}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
