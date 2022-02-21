from typing import Callable

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import ta
import numpy
import pandas as pd


class MacdResults:
    """
    Represents MACD results in macd, signal and hist properties
    each of type :class:`numpy.ndarray`
    with max size of value that was reserved by :class:MACD
    """
    def __init__(
            self,
            macd: numpy.ndarray,
            signal: numpy.ndarray,
            hist: numpy.ndarray
    ):
        self.macd = macd
        self.signal = signal
        self.hist= hist
    # TODO: add lookup param?
    def crossover_up(self) -> bool:
        if not self.hist[-1]:
            return False
        return self.hist[-1] > 0 and self.hist[-2] <= 0

    def crossover_down(self) -> bool:
        if not self.hist[-1]:
            return False
        return self.hist[-1] <= 0 and self.hist[-2] > 0


class MACD(Oscillator):

    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            fastperiod: int=12,
            slowperiod: int=26,
            signalperiod: int=9,
            name: str=None
    ):
        if not name:
            name = f'MACD_{timeframe.name}_{period}'
        self._fastperiod = fastperiod
        self._slowperiod = slowperiod
        self._signalperiod = signalperiod
        self._reserved_size = 300
        super().__init__(market_data, timeframe, name)

    def reserve(self) -> None:
        self._market_data.reserve(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size
        )

    def __call__(self) -> MacdResults:
        close = self._market_data.get(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size)

        close = pd.Series(close)

        macd = ta.trend.MACD(
            close,
            self._slowperiod,
            self._fastperiod,
            self._signalperiod)

        return MacdResults(
            macd.macd().values,
            macd.macd_signal().values,
            macd.macd_diff().values)


def macd(
        timeframe: Timeframes,
        fastperiod: int=12,
        slowperiod: int=26,
        signalperiod: int=9,
        name: str=None
) -> Callable:
    #
    return lambda market_data: MACD(
        market_data, timeframe,
        fastperiod, slowperiod,
        signalperiod, name
    )
