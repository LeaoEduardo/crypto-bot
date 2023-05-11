from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

Base = declarative_base()

class Coin(Base):
  __tablename__ = 'coin'

  id = Column(Integer, primary_key=True)

  # relationships
  klines = relationship("Kline")

  # properties
  name = Column(String, nullable=False)
  ticker = Column(String, nullable=True)

  def __repr__(self):
    return f"<Coin(name={self.name})>"

class Kline(Base):
  __tablename__ = 'kline'

  id = Column(Integer, primary_key=True)

  # relationships
  coin_id = Column(Integer, ForeignKey("coin.id", ondelete="CASCADE"), nullable=False)
  coin = relationship("Coin", back_populates="klines")

  # properties
  open_time = Column(DateTime,nullable=False)
  open_price = Column(Float,nullable=False)
  high_price = Column(Float,nullable=False)
  low_price = Column(Float,nullable=False)
  close_price = Column(Float,nullable=False)
  close_time = Column(DateTime,nullable=False)
  volume = Column(Float,nullable=True)
  quote_asset_volume = Column(Float,nullable=True)
  number_of_trades = Column(Integer,nullable=True)
  taker_buy_base_asset_volume = Column(Float,nullable=True)
  taker_buy_quote_asset_volume = Column(Float,nullable=True)
  

  def __repr__(self):
    return f"<Kline(coin_id={self.coin_id}, open_time={self.open_time}, open_price={self.open_price})>"