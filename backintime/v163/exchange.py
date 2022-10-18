import typing as t
from backintime.v163.broker import Broker
from backintime.v163.data.candle import Candle
from backintime.v163.data.data_provider import DataProvider


class Exchange(Broker):
	def __init__(self, data: DataProvider):
		self._data=data

	def submit_order(self) -> None:
		pass 

	def get_accounts(self) -> float:
		pass

	def get_trades(self) -> list:
		pass

	def candles(self) -> t.Generator[Candle, None, None]:
		for candle in self._data:
			self._update(candle)
			yield candle

	def _update(self, candle: Candle) -> None:
		""" Review whether opened orders can be closed """
		pass