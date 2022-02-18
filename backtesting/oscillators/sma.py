from typing import Callable

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import talib


class SMA(Oscillator):

    def __init__(
            self, timeframe: Timeframes,
            property: CandleProperties,
            period: int, name: str=None
    ):
        if not name:
            name = f'SMA_{timeframe.name}_{period}'

        self._timeframe = timeframe
        self._property_hint = property
        self._period = period
        #
        self._reserved_size = period
        super().__init__(name)

    def reserve(self) -> None:
        self._market_data.reserve(
            self._timeframe,
            self._property_hint,
            self._reserved_size
        )

    def __call__(self) -> float:
        values = self._market_data.get(
            self._timeframe,
            self._property_hint,
            self._reserved_size
        )

        sma = talib.SMA(values, self._period)[-1]
        return sma


def sma(timeframe: Timeframes,
        property: CandleProperties,
        period: int,
        name: str=None) -> Callable:
    return lambda: SMA(timeframe, property, period, name)
