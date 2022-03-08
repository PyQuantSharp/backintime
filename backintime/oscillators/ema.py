from typing import Callable, Union
from ta.trend import EMAIndicator as EMAIndicator

from .oscillator import Oscillator, DEFAULT_LOOKUP
from .utils import dependency
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import numpy
import pandas as pd


class EMA(Oscillator):

    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            property: CandleProperties,
            period: int,
            name: str=None,
            seq: bool=True
    ):
        name = name or f'EMA_{timeframe.name}_{preiod}'
        deps = dependency(
            (timeframe, property, DEFAULT_LOOKUP))

        self._period = period
        self.seq = seq
        super().__init__(deps, market_data, name)

    def __call__(self) -> Union[numpy.ndarray, float]:
        values = pd.Series(self._get_values())
        ema = EMAIndicator(values, self._period).ema_indicator()
        ema = ema.values

        if not self.seq:
            return ema[-1]
        return ema


def ema(timeframe: Timeframes,
        property: CandleProperties,
        period: int,
        name: str=None,
        seq: bool=True) -> Callable:
    #
    return lambda market_data: EMA(
        market_data, timeframe,
        property, period,
        name, seq
    )
