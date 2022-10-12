import typing as t
import datetime

from backintime.v163.trading_strategy import TradingStrategy
from backintime.v163.exchange import Exchange
from backintime.v163.data import DataProvider


class Backtester:
	def __init__(self, 
				 strategy_t: t.Type[TradingStrategy], 
				 market_data: DataProvider):
		self._exchange = Exchange(market_data)
		self._strategy = strategy_t(broker=self._exchange)

	def run(self, since: datetime.datetime, until: datetime.datetime):
		for candle in self._exchange.candles():
			self._strategy.tick(candle)
		return self._exchange.get_trades() # and wrap to `Result` with IO methods