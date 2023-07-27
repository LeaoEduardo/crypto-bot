import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from tqdm import tqdm
from binance import Client
import pandas as pd
import numpy as np
from metaflow import FlowSpec, step, Parameter

load_dotenv(".env")

BINANCE_API = os.environ.get('BINANCE_API', None)
BINANCE_SECRET = os.environ.get('BINANCE_SECRET', None)

class CryptoInfoFlow(FlowSpec):

    @staticmethod
    def convert_timestamp_column(x):
        return dt.fromtimestamp(x / 1000)

    @step
    def start(self):
        test = False
        self.coins = []
        self.client = Client(BINANCE_API, BINANCE_SECRET)
        if test:
            self.client.API_URL = 'https://testnet.binance.vision/api'
        self.next(self.get_exchange_info)

    @step
    def get_exchange_info(self):
        exchange_info = pd.DataFrame.from_records(self.client.get_exchange_info()['symbols'])
        if not self.coins:
            self.coins = exchange_info.baseAsset.unique()
        self.exchange_info = exchange_info

        # Use NumPy to split the coins list into n_batches sublists
        self.batches = np.array_split(self.coins, self.n_batches)
        self.next(self.process_batches, foreach='batches')

    @step
    def process_batches(self):
        def get_crypto_info(client, coin_name, exchange_info, interval='1d', start_date=dt.now()-relativedelta(days=self.TIMESPAN)):
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

        batch_coins = self.input

        # Iterate over the coins in the current batch and get their data
        dfs = []
        for coin in tqdm(batch_coins):
            crypto_info = get_crypto_info(self.client, coin, self.exchange_info)
            if crypto_info is not None:
                dfs.append(crypto_info)

        # Concatenate the DataFrames of the current batch
        self.combined_df = pd.concat(dfs, ignore_index=True)
        self.next(self.join)

    @step
    def join(self, inputs):
        self.dfs = [input.combined_df for input in inputs]
        self.next(self.save_data)

    @step
    def save_data(self):
        import os
        if not os.path.exists("data"):
            os.mkdir("data")
        pd.concat(self.dfs, ignore_index=True).to_csv("data/crypto_info.csv")
        self.next(self.end)

    @step
    def end(self):
        pass

    # Declare the parameters using the Parameter class
    TIMESPAN = Parameter('TIMESPAN', help='Number of days to fetch historical data', default=30)
    n_batches = Parameter('n_batches', help='Number of batches to split the coins list', default=20)

if __name__ == '__main__':
    CryptoInfoFlow()  # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
