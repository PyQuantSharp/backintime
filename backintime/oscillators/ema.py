from typing import Callable, Union
from ta.trend import EMAIndicator as EMAIndicator

from .oscillator import Oscillator
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
        if not name:
            name = f'EMA_{timeframe.name}_{period}'
        self._property_hint = property
        self._period = period
        self._reserved_size = 100
        self.seq = seq
        super().__init__(market_data, timeframe, name)

    def reserve(self) -> None:
        self._market_data.reserve(
            self._timeframe,
            self._property_hint,
            self._reserved_size
        )

    def __call__(self) -> Union[numpy.ndarray, float]:
        values = self._market_data.get(
            self._timeframe,
            self._property_hint,
            self._reserved_size)

        values = pd.Series(values)
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
