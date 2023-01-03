import ta
import numpy
import pandas as pd
import typing as t
from backintime.timeframes import Timeframes
from .constants import CandleProperties, CLOSE
from .base import (
    MarketData,
    BaseIndicator, 
    IndicatorFactory, 
    IndicatorParam
)


class SMAIndicator(BaseIndicator):
    def __init__(self, 
                 market_data: MarketData,
                 timeframe: Timeframes,
                 candle_property: CandleProperties,
                 period: int):
        self._timeframe = timeframe
        self._candle_property = candle_property
        self._period = period
        super().__init__(market_data)

    def __call__(self) -> numpy.ndarray:
        market_data = self.market_data
        tf = self._timeframe
        qty = self._period
        values = market_data.get_values(tf, self._candle_property, qty)
        values = pd.Series(values)
        sma = ta.trend.SMAIndicator(values, self._period).sma_indicator()
        return sma.values


class SMAFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 candle_property: CandleProperties = CLOSE,
                 period: int = 9,
                 name: str = ''):
        self.timeframe = timeframe
        self.candle_property = candle_property
        self.period = period
        self._name = name or f"sma_{str.lower(timeframe.name)}"

    @property
    def indicator_name(self) -> str:
        return self._name

    @property
    def indicator_params(self) -> t.Sequence[IndicatorParam]:
        return [
            IndicatorParam(timeframe=self.timeframe, 
                           candle_property=self.candle_property,
                           quantity=self.period)
        ]

    def create(self, data: MarketData) -> SMAIndicator:
        return SMAIndicator(data, self.timeframe, 
                            self.candle_property, self.period)

