import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def load(
  connection_url: str = "postgresql://postgres:postgres@0.0.0.0:5432/crypto",
  csv_path: str = "crypto_info.csv"
):
  from db.schema import Kline, Coin
  
  dataframe = pd.read_csv(csv_path, index_col=0),
  engine = create_engine(connection_url, echo=True)

  with Session(engine) as session:
    for row in dataframe.itertuples(index=False):
      coin = Coin(
        name = row.coin_name,
        ticker = row.ticker,
      )
      kline = Kline(
        coin = coin,
        open_time = row.open_time,
        open_price = row.open_price,
        high_price = row.high_price,
        low_price = row.low_price,
        close_price = row.close_price,
        volume = row.volume,
        close_time = row.close_time,
        quote_asset_volume = row.quote_asset_volume,
        number_of_trades = row.number_of_trades,
        taker_buy_base_asset_volume = row.taker_buy_base_asset_volume,
        taker_buy_quote_asset_volume = row.taker_buy_quote_asset_volume,
      )
      session.add(kline)
    session.commit()

if __name__ == '__main__':
  load()