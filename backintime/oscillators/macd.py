from typing import Callable

from .oscillator import Oscillator, DEFAULT_LOOKUP
from .utils import dependency
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
        name = name or f'MACD_{timeframe.name}'
        deps = dependency(
            (timeframe, CandleProperties.CLOSE, DEFAULT_LOOKUP))

        self._fastperiod = fastperiod
        self._slowperiod = slowperiod
        self._signalperiod = signalperiod

        super().__init__(deps, market_data, name)

    def __call__(self) -> MacdResults:
        close = pd.Series(self._get_values())
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
