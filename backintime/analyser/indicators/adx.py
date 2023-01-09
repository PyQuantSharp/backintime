import ta
import numpy
import pandas as pd
import typing as t
from backintime.timeframes import Timeframes
from .constants import HIGH, LOW, CLOSE
from .base import (
    MarketData,
    BaseIndicator, 
    IndicatorFactory, 
    IndicatorParam
)


class ADXIndicator(BaseIndicator):
    def __init__(self, 
                 market_data: MarketData,
                 timeframe: Timeframes,
                 period: int):
        self._timeframe = timeframe
        self._period = period
        self._quantity = period**2
        super().__init__(market_data)

    def __call__(self) -> numpy.ndarray:
        market_data = self.market_data
        timeframe = self._timeframe
        qty = self._quantity

        highs = market_data.get_values(timeframe, HIGH, qty)
        highs = pd.Series(highs, dtype=numpy.float64)
        
        lows = market_data.get_values(timeframe, LOW, qty)
        lows = pd.Series(lows, dtype=numpy.float64)

        close = market_data.get_values(timeframe, CLOSE, qty)
        close = pd.Series(close, dtype=numpy.float64)

        adx = ta.trend.adx(highs, lows, close, self._period)
        return adx.values


class ADXFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 period: int = 14,
                 name: str = ''):
        self.timeframe = timeframe
        self.period = period
        self._name = name or f"adx_{str.lower(timeframe.name)}"

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

    def create(self, data: MarketData) -> ADXIndicator:
        return ADXIndicator(data, self.timeframe, self.period)
