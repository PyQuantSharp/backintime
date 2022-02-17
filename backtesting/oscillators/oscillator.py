from __future__ import annotations
from abc import ABC, abstractmethod
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage


class Oscillator(ABC):

    def __init__(self, name):
        self._name = name

    def get_name(self) -> str:
        return self._name

    def set_market_data(self, market_data: MarketDataStorage) -> Oscillator:
        self._market_data = market_data
        self.reserve()
        return self

    @abstractmethod
    def reserve(self) -> None:
        pass

    @abstractmethod
    def __call__(self):
        pass
