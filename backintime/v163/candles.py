import typing as t

from backintime.v163.data.data_provider import Candle
from backintime.v163.timeframes import Timeframes as tf


class CandlesBuffer:
	def get(self, timeframe: tf) -> Candle:
		pass 

	def update(self, candle: Candle, ticks: int) -> None:
		pass


class Candles:
	def __init__(self, timeframes: t.Iterable[tf], buffer: CandlesBuffer):
		self._data = { 
			timeframe: Candle(open_time=None,
							  open=0, high=0,
							  low=0, close=0,
							  volume=0,
							  close_time=None)
				for timeframe in timeframes 
		} 

	def get(self, timeframe: tf) -> Candle:
		return self._data[timeframe]