from typing import Callable, Union

from .oscillator import Oscillator
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
        if not name:
            name = f'SMA_{timeframe.name}_{period}'
        self._property_hint = property
        self._period = period
        self._reserved_size = period
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
