import pandas as pd
import numpy as np
import sys
sys.path.append('crypto-bot')

from utils.cg_api import CoinGeckoAPI

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


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

    coins_cg = data["symbols"]
    coins_binance = args[0]

    coins = list(filter(lambda cb: cb.lower() in coins_cg, coins_binance))

    cg_api = CoinGeckoAPI()

    coins_dfs = []
    for batch in np.split(coins, [len(coins) // 4, len(coins) // 2, len(coins) * 3 // 2]):
        coins_dfs.append(cg_api.get_multiple_coins_info(coins_list=batch))

    coins_mkt_cap = pd.concat(coins_dfs)

    filtered_mkt_cap = coins_mkt_cap[coins_mkt_cap['usd_market_cap'] >= 1e8]

    upper = np.vectorize(lambda x: x.upper())

    return upper(filtered_mkt_cap.index)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
