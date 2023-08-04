from statsmodels.tsa.stattools import coint
import numpy as np
import json
import os

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

    coins = data.columns

    all_combinations = [[coins[i], coins[j]] for i in range(len(coins)) for j in range(len(coins)) if i != j and j > i]
    combination_pairs = ['-'.join(combination) for combination in all_combinations]

    p_values = {}
    combination_pairs_size = len(combination_pairs)
    print("Verifying p-values for", combination_pairs_size, "pairs...")
    for i, combination_pair in enumerate(combination_pairs):
        if i == combination_pairs_size//2: print(f"Halfway there ({i})...")
        coins_data = data[combination_pair.split('-')].dropna()
        p_value = coint(coins_data.iloc[:, 0], coins_data.iloc[:, 1])[1]
        p_values[combination_pair] = p_value

    cointegrations = list(filter(lambda x: x[1] <= 0.05, p_values.items()))

    pairs = [pair[0].split('-') for pair in cointegrations]
    coins = list(np.unique(np.array(pairs).flatten()))


    with open(f"mage_data/crypto-bot/coints.json", "w") as f:
        json.dump(cointegrations, f)

    return data[coins]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
