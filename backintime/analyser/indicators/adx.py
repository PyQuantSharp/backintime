import ta
import numpy
import pandas as pd
import typing as t
from backintime.timeframes import Timeframes
from .base import MarketData, IndicatorParam
from .constants import HIGH, LOW, CLOSE



def adx(market_data: MarketData, 
        timeframe: Timeframes,
        period: int = 14) -> numpy.ndarray:
    """
    Average Directional Movement Index (ADX).

    ADX does not indicate trend direction or momentum, 
    only trend strength. 
    Generally, ADX readings below 20 indicate trend weakness,
    and readings above 40 indicate trend strength. 
    An extremely strong trend is indicated by readings above 50.
    """
    quantity = period**2

    highs = market_data.get_values(timeframe, HIGH, quantity)
    highs = pd.Series(highs, dtype=numpy.float64)
        
    lows = market_data.get_values(timeframe, LOW, quantity)
    lows = pd.Series(lows, dtype=numpy.float64)

    close = market_data.get_values(timeframe, CLOSE, quantity)
    close = pd.Series(close, dtype=numpy.float64)

    adx = ta.trend.adx(highs, lows, close, period)
    return adx.values


def adx_params(timeframe: Timeframes, 
               period: int = 14) -> t.Tuple[IndicatorParam]:
    """Get list of ADX params."""
    return (
        IndicatorParam(timeframe, HIGH, period**2),
        IndicatorParam(timeframe, LOW, period**2),
        IndicatorParam(timeframe, CLOSE, period**2)
    )