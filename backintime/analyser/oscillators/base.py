import typing as t

from abc import ABC, abstractmethod
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CandleProperties

# NOTE: in < 3.9 can't use collections.abc mixins with type subscruptions
ResultItem = t.TypeVar("ResultItem")

class OscillatorResultSequence(t.Generic[ResultItem]):
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


class Oscillator(ABC):
    @abstractmethod
    def __call__(self) -> OscillatorResultSequence:
        pass


class MarketData(ABC):
    @abstractmethod
    def get_values(self, 
                   timeframe: Timeframes, 
                   candle_property: CandleProperties, 
                   quantity: int):
        pass


class BaseOscillator(Oscillator):
    def __init__(self, market_data: MarketData):
        self._market_data = market_data

    @property
    def market_data(self) -> MarketData:
        return self._market_data


@dataclass
class OscillatorParam:
    timeframe: Timeframes
    candle_property: CandleProperties
    quantity: t.Optional[int] = None


class OscillatorFactory(ABC):
    @abstractmethod
    def get_oscillator_name(self) -> str:
        """
        Get the name of the oscillator to be created.
        Instances with different timeframes must have different names.
        """
        pass

    @abstractmethod
    def get_oscillator_params(self) -> t.Sequence[OscillatorParam]:
        """Get a list of params of the oscillator to be created."""
        pass

    @abstractmethod
    def create(self, market_data: MarketData) -> BaseOscillator:
        pass
