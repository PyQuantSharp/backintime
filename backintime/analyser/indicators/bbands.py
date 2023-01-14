import ta
import numpy
import pandas as pd
import typing as t
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CandleProperties, CLOSE
from .base import (
    MarketData,
    BaseIndicator, 
    IndicatorFactory, 
    IndicatorParam,
    IndicatorResultSequence
)


@dataclass
class BbandsResultItem:
    upper_band: numpy.float64
    middle_band: numpy.float64
    lower_band: numpy.float64


class BbandsResultSequence(IndicatorResultSequence[BbandsResultItem]):
    def __init__(self, 
                 upper_band: numpy.ndarray, 
                 middle_band: numpy.ndarray, 
                 lower_band: numpy.ndarray):
        self.upper_band = upper_band
        self.middle_band = middle_band
        self.lower_band = lower_band

    def __iter__(self) -> t.Iterator[BbandsResultItem]:
        zip_iter = zip(self.upper_band, self.middle_band, self.lower_band)
        return (
            BbandsResultItem(upper, middle, lower) 
                for upper, middle, lower in zip_iter
        )

    def __reversed__(self) -> t.Iterator[BbandsResultItem]:
        reversed_iter = zip(reversed(self.upper_band), 
                            reversed(self.middle_band), 
                            reversed(self.lower_band))
        return (
            BbandsResultItem(upper, middle, lower) 
                for upper, middle, lower in reversed_iter
        )

    def __getitem__(self, index: int) -> BbandsResultItem:
        return BbandsResultItem(self.upper_band[index], 
                                self.middle_band[index], 
                                self.lower_band[index])

    def __len__(self) -> int:
        return min(len(self.upper_band), 
                   len(self.middle_band), 
                   len(self.lower_band))

    def __repr__(self) -> str:
        return (f"BbandsResultSequence(upper_band={self.upper_band}, "
                f"middle_band={self.middle_band}, "
                f"lower_band={self.lower_band})")


class BbandsIndicator(BaseIndicator):
    def __init__(self, 
                 market_data: MarketData,
                 timeframe: Timeframes,
                 candle_property: CandleProperties,
                 period: int,
                 deviation_quotient: int):
        self._timeframe = timeframe
        self._candle_property = candle_property
        self._period = period
        self._devq = deviation_quotient
        self._quantity = period**2
        super().__init__(market_data)

    def __call__(self) -> BbandsResultSequence:
        market_data = self.market_data
        tf = self._timeframe
        qty = self._quantity
        values = market_data.get_values(tf, self._candle_property, qty)
        values = pd.Series(values)

        bbands = ta.volatility.BollingerBands(values, 
                                              self._period, 
                                              self._devq)
        upper_band = bbands.bollinger_hband().values
        middle_band = bbands.bollinger_mavg().values
        lower_band = bbands.bollinger_lband().values

        return BbandsResultSequence(upper_band, middle_band, lower_band)


class BbandsFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 candle_property: CandleProperties = CLOSE,
                 period: int = 20,
                 deviation_quotient: int = 2,
                 name: str = ''):
        self.timeframe = timeframe
        self.candle_property = candle_property
        self.period = period
        self.deviation_quotient = deviation_quotient
        self._name = name or f"bbands_{str.lower(timeframe.name)}"

    @property
    def indicator_name(self) -> str:
        return self._name

    @property
    def indicator_params(self) -> t.Sequence[IndicatorParam]:
        return [
            IndicatorParam(timeframe=self.timeframe, 
                           candle_property=self.candle_property,
                           quantity=self.period**2)
        ]

    def create(self, data: MarketData) -> BbandsIndicator:
        return BbandsIndicator(data, self.timeframe, self.candle_property,
                               self.period, self.deviation_quotient)

