import typing as t

from datetime import datetime
from collections import abc
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float
    open_time: datetime
    close_time: datetime
    is_closed: t.Optional[bool]=True


class DataProvider(abc.Iterable):
	@abstractmethod
	def __iter__(self) -> t.Iterator[Candle]:
		pass

