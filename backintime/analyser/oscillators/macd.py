import typing as t

import ta
import numpy
import pandas as pd
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CandleProperties
from .base import (
    Oscillator, 
    MarketData,
    BaseOscillator, 
    OscillatorFactory, 
    OscillatorParam,
    OscillatorResultSequence
)


@dataclass
class MacdResultItem:
    macd: float
    signal: float
    hist: float


class MacdResultSequence(OscillatorResultSequence[MacdResultItem]):
    def __init__(self,
                 macd: numpy.ndarray,
                 signal: numpy.ndarray,
                 hist: numpy.ndarray):
        self.macd = macd
        self.signal = signal
        self.hist = hist

    def crossover_up(self) -> bool:
        return self.hist[-1] > 0 and self.hist[-2] <= 0

    def crossover_down(self) -> bool:
        return self.hist[-1] <= 0 and self.hist[-2] > 0

    def __iter__(self) -> t.Iterator[MacdResultItem]:
        return (
            MacdResultItem(macd, signal, hist) 
                for macd, signal, hist in zip(self.macd, 
                                              self.signal, 
                                              self.hist)
        )

    def __reversed__(self) -> t.Iterator[MacdResultItem]:
        return (
            MacdResultItem(macd, signal, hist) 
                for macd, signal, hist in zip(reversed(self.macd),
                                              reversed(self.signal), 
                                              reversed(self.hist))
        )

    def __getitem__(self, index: int) -> MacdResultItem:
        return MacdResultItem(self.macd[index], 
                              self.signal[index], 
                              self.hist[index])

    def __repr__(self) -> str:
        return (f"MacdResultSequence(macd={self.macd}, "
                f"signal={self.signal}, hist={self.hist})")


class Macd(BaseOscillator):
    def __init__(self, 
                 market_data: MarketData,
                 timeframe: Timeframes,
                 fastperiod: int=12,
                 slowperiod: int=26,
                 signalperiod: int=9):
        self._timeframe = timeframe
        self._fastperiod = fastperiod
        self._slowperiod = slowperiod
        self._signalperiod = signalperiod
        super().__init__(market_data)

    def __call__(self) -> MacdResultSequence:
        market_data = self.market_data
        close = pd.Series(market_data.get_values(self._timeframe,
                                                 CandleProperties.CLOSE,
                                                 100))
        macd = ta.trend.MACD(close,
                             self._slowperiod,
                             self._fastperiod,
                             self._signalperiod)

        return MacdResultSequence(macd.macd().values,
                                  macd.macd_signal().values,
                                  macd.macd_diff().values)


class MacdFactory(OscillatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 fastperiod: int=12,
                 slowperiod: int=26,
                 signalperiod: int=9):
        self.timeframe = timeframe
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod

    def get_oscillator_name(self) -> str:
        return f"macd_{str.lower(self.timeframe.name)}"

    def get_oscillator_params(self) -> t.Sequence[OscillatorParam]:
        return [
            OscillatorParam(self.timeframe, CandleProperties.CLOSE)
        ]

    def create(self, data) -> Macd:
        return Macd(data, self.timeframe, self.fastperiod, 
                    self.slowperiod, self.signalperiod)

