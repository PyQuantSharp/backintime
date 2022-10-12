import typing as t
from backintime.v163.broker import Broker
from backintime.v163.data import DataProvider, Candle


class Exchange(Broker):
	def __init__(self, data: DataProvider):
		self._data=data

	def submit_order(self) -> None:
		pass 

	def get_accounts(self) -> float:
		pass

	def candles(self) -> t.Generator[Candle]:
		for candle in self._data:
			self._update(candle)
			yield candle

	def _update(self, candle: Candle) -> None:
		""" Review whether opened orders can be closed """
		pass