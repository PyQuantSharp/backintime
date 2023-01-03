import ta
import numpy
import pandas as pd
import typing as t
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CandleProperties
from .base import (
    MarketData,
    BaseIndicator, 
    IndicatorFactory, 
    IndicatorParam,
    IndicatorResultSequence
)


@dataclass
class MacdResultItem:
    macd: numpy.float64
    signal: numpy.float64
    hist: numpy.float64


class MacdResultSequence(IndicatorResultSequence[MacdResultItem]):
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
        zip_iter = zip(self.macd, self.signal, self.hist)
        return (
            MacdResultItem(macd, signal, hist) 
                for macd, signal, hist in zip_iter
        )

    def __reversed__(self) -> t.Iterator[MacdResultItem]:
        reversed_iter = zip(reversed(self.macd), 
                            reversed(self.signal), 
                            reversed(self.hist))
        return (
            MacdResultItem(macd, signal, hist) 
                for macd, signal, hist in reversed_iter
        )

    def __getitem__(self, index: int) -> MacdResultItem:
        return MacdResultItem(self.macd[index], 
                              self.signal[index], 
                              self.hist[index])

    def __repr__(self) -> str:
        return (f"MacdResultSequence(macd={self.macd}, "
                f"signal={self.signal}, hist={self.hist})")


class MacdIndicator(BaseIndicator):
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
        self._quantity = signalperiod * slowperiod
        super().__init__(market_data)

    def __call__(self) -> MacdResultSequence:
        market_data = self.market_data
        close = pd.Series(market_data.get_values(self._timeframe,
                                                 CandleProperties.CLOSE,
                                                 self._quantity))
        macd = ta.trend.MACD(close,
                             self._slowperiod,
                             self._fastperiod,
                             self._signalperiod)

        return MacdResultSequence(macd.macd().values,
                                  macd.macd_signal().values,
                                  macd.macd_diff().values)


class MacdFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 fastperiod: int=12,
                 slowperiod: int=26,
                 signalperiod: int=9,
                 name: str = ''):
        self.timeframe = timeframe
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod
        self._name = name or f"macd_{str.lower(timeframe.name)}"

    @property
    def indicator_name(self) -> str:
        return self._name

    @property
    def indicator_params(self) -> t.Sequence[IndicatorParam]:
        return [
            IndicatorParam(timeframe=self.timeframe, 
                           candle_property=CandleProperties.CLOSE,
                           quantity=self.slowperiod * self.signalperiod)
        ]

    def create(self, data: MarketData) -> MacdIndicator:
        return MacdIndicator(data, self.timeframe, self.fastperiod, 
                             self.slowperiod, self.signalperiod)

