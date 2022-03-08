from typing import Callable, Union
from ta.momentum import RSIIndicator as RSIIndicator

from .oscillator import Oscillator, DEFAULT_LOOKUP
from .utils import dependency
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
            name: str=None,
            seq: bool=True
    ):
        name = name or f'RSI_{timeframe.name}_{period}'
        deps = dependency(
            (timeframe, CandleProperties.CLOSE, period))

        self._period = period
        self.seq = seq
        super().__init__(deps, market_data, name)

    def __call__(self) -> Union[numpy.ndarray, float]:
        close = pd.Series(self._get_values())
        rsi = RSIIndicator(close, self._period).rsi()
        rsi = rsi.values

        if not self.seq:
            return rsi[-1]
        return rsi


def rsi(timeframe: Timeframes,
        period: int=14,
        name: str=None,
        seq: bool=True) -> Callable:
    #
    return lambda market_data: RSI(
        market_data, timeframe,
        period, name, seq
    )
