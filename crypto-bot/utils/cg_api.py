import requests
import pandas as pd
from datetime import datetime as dt

class CoinGeckoAPI():

  def __init__(self, base_url = 'https://api.coingecko.com/api/v3', vs_currency='usd'):
    self.base_url = base_url
    self.vs_currency = vs_currency

  def get_all_coins(self) -> pd.DataFrame:
    response = requests.get(f'{self.base_url}/coins/list').json()
    return pd.DataFrame.from_records(response)

  def get_all_categories(self) -> pd.DataFrame:
    response = requests.get(f'{self.base_url}/coins/categories/list').json()
    return pd.DataFrame.from_records(response)

  def get_coins_from_category(self, category_id) -> pd.DataFrame:
    response = requests.get(f'{self.base_url}/coins/markets?vs_currency={self.vs_currency}&category={category_id}').json()
    return pd.DataFrame.from_records(response)

  def get_historical_data(self, coin_id, begin: dt, end: dt) -> pd.DataFrame:
    begin_ts = time.mktime(begin.timetuple())
    end_ts = time.mktime(end.timetuple())
    response = requests.get(f'{self.base_url}/coins/{coin_id}/market_chart/range?vs_currency={self.vs_currency}&from={begin_ts}&to={end_ts}').json()
    return pd.DataFrame.from_records(response)

  def get_multiple_coins_info(self, coins_list) -> pd.DataFrame:
    str_coin_list = ''
    for id in coins_list:
      str_coin_list += id + ','
    str_coin_list = str_coin_list.rstrip(',')
    response = requests.get(f'{self.base_url}/simple/price?ids={str_coin_list}&vs_currencies={self.vs_currency}&include_market_cap=true&include_24hr_vol=true').json()
    return pd.DataFrame.from_records(response).T

  def get_trending_coins(self) -> pd.DataFrame:
    response = requests.get(f'{self.base_url}/search/trending').json()['coins']
    records = [resp['item'] for resp in response]
    return pd.DataFrame.from_records(records)