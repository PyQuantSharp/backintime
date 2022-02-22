from typing import Callable, Union
from ta.volatility import AverageTrueRange as AverageTrueRange

from .oscillator import Oscillator
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
        if not name:
            name = f'ATR_{timeframe.name}_{period}'
        self._period = period
        self._reserved_size = 300
        self.seq = seq
        super().__init__(market_data, timeframe, name)

    def reserve(self) -> None:
        # TODO: consider change .reserve to accept list of properties
        self._market_data.reserve(
            self._timeframe,
            CandleProperties.HIGH,
            self._reserved_size)

        self._market_data.reserve(
            self._timeframe,
            CandleProperties.LOW,
            self._reserved_size)

        self._market_data.reserve(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size)

    def __call__(self) -> Union[numpy.ndarray, float]:
        high = self._market_data.get(
            self._timeframe,
            CandleProperties.HIGH,
            self._reserved_size)
        high = pd.Series(high)

        low = self._market_data.get(
            self._timeframe,
            CandleProperties.LOW,
            self._reserved_size)
        low = pd.Series(low)

        close = self._market_data.get(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size)
        close = pd.Series(close)

        atr = AverageTrueRange(
            high,
            low,
            close,
            self._period
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
