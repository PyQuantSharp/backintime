import ta
import numpy
import pandas as pd
import typing as t
from backintime.timeframes import Timeframes
from .constants import CandleProperties, CLOSE
from .base import MarketData, IndicatorParam


def sma(market_data: MarketData, 
        timeframe: Timeframes,
        candle_property: CandleProperties = CLOSE,
        period: int = 9) -> numpy.ndarray:
    """Simple moving average, also known as 'MA'."""
    values = market_data.get_values(timeframe, candle_property, period)
    values = pd.Series(values)
    sma = ta.trend.SMAIndicator(values, period).sma_indicator()
    return sma.values


def sma_params(timeframe: Timeframes,
               candle_property: CandleProperties = CLOSE,
               period: int = 9) -> t.Tuple[IndicatorParam]:
    """Get list of SMA params."""
    return (
        IndicatorParam(timeframe=timeframe, 
                       candle_property=candle_property,
                       quantity=period),
    )