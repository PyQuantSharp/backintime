import typing as t
from backintime.v163.broker import Broker
from backintime.v163.data.candle import Candle
from backintime.v163.data.data_provider import DataProvider


class Exchange(Broker):
	def __init__(self, data: DataProvider):
		self._data=data

	def candles(self) -> t.Generator[Candle, None, None]:
		for candle in self._data:
			self._update(candle)
			yield candle

	def _update(self, candle: Candle) -> None:
		""" Review whether opened orders can be closed """
		pass