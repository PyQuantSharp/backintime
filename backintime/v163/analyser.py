import typing as t

from backintime.v163.data.data_provider import Candle
from backintime.v163.oscillators import Oscillator
from backintime.v163.timeframes import Timeframes as tf


class AnalyserBuffer:
	def update(self, candle: Candle, ticks: int) -> None:
		pass


class Analyser:
	def __init__(self, 
				 oscillators: t.Iterable[Oscillator], 
				 buffer: AnalyserBuffer):
		self._buffer = buffer
		self._oscillators = {
			oscillator.get_name() : oscillator 
				for oscillator in oscillators
		}
	
	def get(self, name: str, timeframe: tf) -> list:
		""" Get list of oscillator values """
		pass

	def get_last(self, name: str, timeframe: tf) -> t.Any:
		""" Get last oscillator value """
		pass