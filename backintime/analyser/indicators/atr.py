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


class ATRIndicator(BaseIndicator):
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
        highs = pd.Series(highs)
        
        lows = market_data.get_values(timeframe, LOW, qty)
        lows = pd.Series(lows)

        close = market_data.get_values(timeframe, CLOSE, qty)
        close = pd.Series(close)

        atr = ta.volatility.AverageTrueRange(highs, lows, 
                                             close, self._period)
        return atr.average_true_range().values


class ATRFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 period: int = 14,
                 name: str = ''):
        self.timeframe = timeframe
        self.period = period
        self._name = name or f"atr_{str.lower(timeframe.name)}"

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

    def create(self, data: MarketData) -> ATRIndicator:
        return ATRIndicator(data, self.timeframe, self.period)
