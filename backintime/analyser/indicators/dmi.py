import ta
import numpy
import pandas as pd
import typing as t
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import HIGH, LOW, CLOSE
from .base import (
    MarketData,
    BaseIndicator, 
    IndicatorFactory, 
    IndicatorParam,
    IndicatorResultSequence
)


@dataclass
class DMIResultItem:
    adx: numpy.float64
    positive_di: numpy.float64
    negative_di: numpy.float64


class DMIResultSequence(IndicatorResultSequence[DMIResultItem]):
    def __init__(self, 
                 adx: numpy.ndarray, 
                 positive_di: numpy.ndarray, 
                 negative_di: numpy.ndarray):
        self.adx = adx
        self.positive_di = positive_di
        self.negative_di = negative_di

    def crossover_up(self) -> bool:
        return self.positive_di[-1] > self.negative_di[-1] and \
                self.positive_di[-2] <= self.negative_di[-2]

    def crossover_down(self) -> bool:
        return self.negative_di[-1] > self.positive_di[-1] and \
                self.negative_di[-2] <= self.negative_di[-2]

    def adx_increases(self, period: int = 2) -> bool:
        values = self.adx[-period:]
        return all(values[i] < values[i + 1] for i in range(len(values) - 1))

    def adx_decreases(self, period: int = 2) -> bool:
        values = self.adx[-period:]
        return all(values[i] >= values[i + 1] for i in range(len(values) - 1))

    def __iter__(self) -> t.Iterator[DMIResultItem]:
        zip_iter = zip(self.adx, self.positive_di, self.negative_di)
        return (
            DMIResultItem(adx, positive_di, negative_di) 
                for adx, positive_di, negative_di in zip_iter
        )

    def __reversed__(self) -> t.Iterator[DMIResultItem]:
        reversed_iter = zip(reversed(self.adx), 
                            reversed(self.positive_di), 
                            reversed(self.negative_di))
        return (
            DMIResultItem(adx, positive_di, negative_di) 
                for adx, positive_di, negative_di in reversed_iter
        )

    def __getitem__(self, index: int) -> DMIResultItem:
        return DMIResultItem(self.adx[index], 
                             self.positive_di[index], 
                             self.negative_di[index])

    def __repr__(self) -> str:
        return (f"DMIResultSequence(adx={self.adx}, "
                f"positive_di={self.positive_di}, "
                f"negative_di={self.negative_di})")


class DMIIndicator(BaseIndicator):
    def __init__(self, 
                 market_data: MarketData,
                 timeframe: Timeframes,
                 period: int):
        self._timeframe = timeframe
        self._period = period
        self._quantity = period**2
        super().__init__(market_data)

    def __call__(self) -> DMIResultSequence:
        market_data = self.market_data
        timeframe = self._timeframe
        qty = self._quantity

        highs = market_data.get_values(timeframe, HIGH, qty)
        highs = pd.Series(highs, dtype=numpy.float64)

        lows = market_data.get_values(timeframe, LOW, qty)
        lows = pd.Series(lows, dtype=numpy.float64)

        close = market_data.get_values(timeframe, CLOSE, qty)
        close = pd.Series(close, dtype=numpy.float64)

        dmi = ta.trend.ADXIndicator(highs, lows, 
                                    close, self._period)

        return DMIResultSequence(adx=dmi.adx().values, 
                                 positive_di=dmi.adx_pos().values, 
                                 negative_di=dmi.adx_neg().values)


class DMIFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 period: int = 14,
                 name: str = ''):
        self.timeframe = timeframe
        self.period = period
        self._name = name or f"dmi_{str.lower(timeframe.name)}"

    @property
    def indicator_name(self) -> str:
        return self._name

    @property
    def indicator_params(self) -> t.Sequence[IndicatorParam]:
        return [
            IndicatorParam(self.timeframe, HIGH, self.period**2),
            IndicatorParam(self.timeframe, LOW, self.period**2),
            IndicatorParam(self.timeframe, CLOSE, self.period**2)
        ]

    def create(self, data: MarketData) -> DMIIndicator:
        return DMIIndicator(data, self.timeframe, self.period)
