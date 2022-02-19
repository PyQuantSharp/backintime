from typing import Any
from abc import ABC, abstractmethod

from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage


class Oscillator(ABC):
    """
    Base class for all oscillators.
    Implement __call__ and reserve methods
    to have your own oscillator
    """
    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            name: str
    ):
        self._timeframe = timeframe
        self._name = name
        self._market_data = market_data
        self.reserve()

    def get_name(self) -> str:
        return self._name

    @abstractmethod
    def reserve(self) -> None:
        """
        This method is used to reserve
        lookup space for OHLC values.
        See :class:`MarketDataStorage` for details
        """
        pass

    @abstractmethod
    def __call__(self) -> Any:
        """
        Runs each time a new candle closes
        Should return an up-to-date oscillator' value
        """
        pass
