import typing as t

from collections import abc
from abc import abstractmethod
from backintime.v163.timeframes import Timeframes
from .candle import Canlde


class DataProvider(abc.Iterable):
    @abstractmethod
    def timeframe(self) -> Timeframes:
        pass
        
	@abstractmethod
	def __iter__(self) -> t.Iterator[Candle]:
		pass

