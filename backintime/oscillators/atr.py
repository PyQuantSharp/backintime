from typing import Callable, Union
from ta.volatility import AverageTrueRange as AverageTrueRange

from .oscillator import Oscillator, DEFAULT_LOOKUP
from .utils import dependency
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import numpy
import pandas as pd


class ATR(Oscillator):

    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            period: int,
            name: str=None,
            seq: bool=True
    ):
        name = name or f'ATR_{timeframe.name}_{period}'

        deps = dependency(
            ( timeframe, CandleProperties.HIGH, DEFAULT_LOOKUP ),
            ( timeframe, CandleProperties.LOW, DEFAULT_LOOKUP ),
            ( timeframe, CandleProperties.CLOSE, DEFAULT_LOOKUP )
        )
        self._period = period
        self.seq = seq
        super().__init__(deps, market_data, name)

    def __call__(self) -> Union[numpy.ndarray, float]:
        high, low, close = list(map(
            lambda x: pd.Series(x), self._get_values()))

        atr = AverageTrueRange(
            high, low,
            close, self._period
        ).average_true_range().values

        if not self.seq:
            return atr[-1]
        return atr


def atr(
        timeframe: Timeframes,
        period: int=14,
        name: str=None,
        seq: bool=True
) -> Callable:
    #
    return lambda market_data: ATR(
        market_data, timeframe,
        period, name, seq)
