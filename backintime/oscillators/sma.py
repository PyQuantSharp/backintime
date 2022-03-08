from typing import Callable, Union

from .oscillator import Oscillator, DEFAULT_LOOKUP
from .utils import dependency
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import ta
import numpy
import pandas as pd


class SMA(Oscillator):

    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            property: CandleProperties,
            period: int,
            name: str=None,
            seq: bool=True
    ):
        name = name or f'SMA_{timeframe.name}_{period}'
        deps = dependency(
            (timeframe, property, DEFAULT_LOOKUP))

        self._period = period
        self.seq = seq
        super().__init__(deps, market_data, name)

    def __call__(self) -> Union[numpy.ndarray, float]:
        values = pd.Series(self._get_values())
        sma = ta.trend.SMAIndicator(values, self._period).sma_indicator()
        sma = sma.values

        if not self.seq:
            return sma[-1]
        return sma


def sma(timeframe: Timeframes,
        property: CandleProperties,
        period: int,
        name: str=None
        seq: bool=True) -> Callable:
    #
    return lambda market_data: SMA(
        market_data, timeframe,
        property, period,
        name, seq
    )
