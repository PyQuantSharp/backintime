from abc import ABC, abstractmethod

from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage


class Oscillator(ABC):

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
        pass

    @abstractmethod
    def __call__(self) -> None:
        pass
