import ta
import numpy
import pandas as pd
import typing as t
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CLOSE
from .base import ( 
    MarketData,
    BaseIndicator, 
    IndicatorFactory, 
    IndicatorParam
)


class RSIIndicator(BaseIndicator):
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
        qty = self._quantity
        close = market_data.get_values(self._timeframe, CLOSE, qty)
        close = pd.Series(close)
        rsi = ta.momentum.RSIIndicator(close, self._period).rsi()
        return rsi.values


class RSIFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 period: int = 14,
                 name: str = ''):
        self.timeframe = timeframe
        self.period = period
        self._name = name or f"rsi_{str.lower(timeframe.name)}"

    @property
    def indicator_name(self) -> str:
        return self._name

    @property
    def indicator_params(self) -> t.Sequence[IndicatorParam]:
        return [
            IndicatorParam(timeframe=self.timeframe, 
                           candle_property=CLOSE,
                           quantity=self.period**2)
        ]

    def create(self, data) -> RSIIndicator:
        return RSIIndicator(data, self.timeframe, self.period)