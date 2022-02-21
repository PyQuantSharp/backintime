from typing import Callable

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import talib


class ATR(Oscillator):

    def __init__(
        self, market_data: MarketDataStorage,
        timeframe: Timeframes, period: int, name: str=None
    ):
        if not name:
            name = f'ATR_{timeframe.name}_{period}'
        self._period = period
        self._reserved_size = 300
        super().__init__(market_data, timeframe, name)

    def reserve(self) -> None:
        # TODO: consider change .reserve to accept list of properties
        self._market_data.reserve(
            self._timeframe,
            CandleProperties.HIGH,
            self._reserved_size
        )
        self._market_data.reserve(
            self._timeframe,
            CandleProperties.LOW,
            self._reserved_size
        )
        self._market_data.reserve(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size
        )

    def __call__(self) -> float:
        high = self._market_data.get(
            self._timeframe,
            CandleProperties.HIGH,
            self._reserved_size
        )
        low = self._market_data.get(
            self._timeframe,
            CandleProperties.LOW,
            self._reserved_size
        )
        close = self._market_data.get(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size
        )

        atr = talib.ATR(high, low, close, self._period)[-1]
        return atr


def atr(timeframe: Timeframes, period: int, name: str=None) -> Callable:
    return lambda market_data: ATR(market_data, timeframe, period, name)
