import typing as t

from backintime.v163.data.candle import Candle
from backintime.v163.timeframes import Timeframes as tf


class CandlesBuffer:
    def __init__(self, timeframes: t.Iterable[tf], base_timeframe: tf):
        self._base_timeframe = base_timeframe
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

	def update(self, candle: Candle, ticks: int) -> None:
		for timeframe in self._data:
            self._update_candle(timeframe, candle, ticks), 

    def _update_candle(self, 
                       timeframe: tf, 
                       new_candle: Candle, 
                       ticks: int) -> None:
        candle = self.get(timeframe)
        ratio = timeframe.value/self._base_timeframe.value
        remainder = ticks % ratio 
        
        if not remainder:
            candle.open_time = new_candle.open_time
            candle.open = new_candle.open 
            candle.high = new_candle.high
            candle.low = new_candle.low
            candle.close = new_candle.close
        else:
            candle.high = max(candle.high, new_candle.high)
            candle.low = min(candle.low, new_candle.low)
            candle.close = new_candle.close
        candle.is_closed = (ratio - remainder == 1)


class Candles:
	def __init__(self, buffer: CandlesBuffer):
		self._buffer=buffer

	def get(self, timeframe: tf) -> Candle:
		return self._buffer.get(timeframe)
        