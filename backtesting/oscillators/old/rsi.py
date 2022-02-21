from typing import Callable

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import talib


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

    def __call__(self) -> float:
        close = self._market_data.get(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size
        )
        rsi = talib.RSI(close, self._period)[-1]
        return rsi


def rsi(timeframe: Timeframes, period: int, name: str=None) -> Callable:
    return lambda market_data: RSI(market_data, timeframe, period, name)
