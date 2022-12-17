import typing as t

from collections import abc
from abc import ABC, abstractmethod
from datetime import datetime
from backintime.timeframes import Timeframes
from .candle import Candle


class DataProvider(abc.Iterable):
    @property
    @abstractmethod
    def symbol(self) -> str:
        pass

    @property
    @abstractmethod
    def timeframe(self) -> Timeframes:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @abstractmethod
    def __iter__(self) -> t.Iterator[Candle]:
        pass


class DataProviderFactory(ABC):
    @property
    @abstractmethod
    def timeframe(self) -> Timeframes:
        pass

    @abstractmethod
    def create(self, since: datetime, until: datetime):
        pass


class DataProviderError(Exception):
    pass

