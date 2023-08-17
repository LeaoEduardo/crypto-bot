from sklearn import preprocessing
import pandas as pd

def normalize(df: pd.DataFrame, method:str='std'):
  if method == 'min_max':
    scaler = preprocessing.MinMaxScaler()
    return pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index), scaler
  if method == 'pct_cumsum':
    return df.pct_change().cumsum().dropna(), None
  if method == 'pct':
    return df.pct_change().dropna(), None
  if method == 'std':
    scaler = preprocessing.StandardScaler()
    return pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index), scaler
  if method == 'None':
    return df, None