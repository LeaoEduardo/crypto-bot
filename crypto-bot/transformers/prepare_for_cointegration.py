import pandas as pd

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
    
    reduced_df = data[['open_time', 'open_price','coin_name']]
    coins = data.coin_name.unique()

    dfs = []
    for coin in coins:
        dfs.append(
            reduced_df[reduced_df['coin_name']==coin].
            rename(columns={'open_price':coin}).
            set_index('open_time').
            drop(columns=['coin_name'])
        )
        
    return pd.concat(dfs, axis=1).astype(float).dropna(axis=1)

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'