from typing import Callable
from ta.momentum import RSIIndicator as RSIIndicator

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import numpy
import pandas as pd


class RSI(Oscillator):

    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            period: int,
            name: str=None
    ):
        if not name:
            name = f'RSI_{timeframe.name}_{period}'
        self._period = period
        self._reserved_size = 300
        super().__init__(market_data, timeframe, name)

    def reserve(self) -> None:
        self._market_data.reserve(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size
        )

    def __call__(self) -> numpy.ndarray:
        close = self._market_data.get(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size)

        close = pd.Series(close)
        rsi = RSIIndicator(close, self._period).rsi()
        return rsi.values


def rsi(timeframe: Timeframes,
        period: int=14,
        name: str=None) -> Callable:
    #
    return lambda market_data: RSI(market_data, timeframe, period, name)
