import numpy as np
import typing as t
from collections import abc
from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CandleProperties

# NOTE: in < 3.9 can't use collections.abc mixins with type subscriptions
ResultItem = t.TypeVar("ResultItem")

class IndicatorResultSequence(abc.Sequence, t.Generic[ResultItem]):
    @abstractmethod
    def __iter__(self) -> t.Iterator[ResultItem]:
        """Iterate over results in historical order: oldest first."""
        pass

    @abstractmethod
    def __reversed__(self) -> t.Iterator[ResultItem]:
        """Iterate over results in reversed order: most recent first."""
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> ResultItem:
        """Get result item by index."""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Get length."""
        pass


class MarketData(ABC):
    @abstractmethod
    def get_values(self, 
                   timeframe: Timeframes, 
                   candle_property: CandleProperties, 
                   limit: int) -> t.Sequence[Decimal]:
        pass


@dataclass(frozen=True)
class IndicatorParam:
    timeframe: Timeframes
    candle_property: CandleProperties
    quantity: int

