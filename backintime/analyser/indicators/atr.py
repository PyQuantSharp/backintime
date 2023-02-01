import ta
import numpy
import pandas as pd
import typing as t
from backintime.timeframes import Timeframes
from .constants import HIGH, LOW, CLOSE
from .base import MarketData, IndicatorParam


def atr(market_data: MarketData, 
        timeframe: Timeframes, 
        period: int = 14) -> numpy.ndarray:
    """Average True Range (ATR)."""
    quantity = period**2

    highs = market_data.get_values(timeframe, HIGH, quantity)
    highs = pd.Series(highs)
        
    lows = market_data.get_values(timeframe, LOW, quantity)
    lows = pd.Series(lows)

    close = market_data.get_values(timeframe, CLOSE, quantity)
    close = pd.Series(close)

    atr = ta.volatility.AverageTrueRange(highs, lows, close, period)
    return atr.average_true_range().values


def atr_params(timeframe: Timeframes, 
               period: int = 14) -> t.Tuple[IndicatorParam]:
    """Get list of ATR params."""
    return (
        IndicatorParam(timeframe, HIGH, period**2),
        IndicatorParam(timeframe, LOW, period**2),
        IndicatorParam(timeframe, CLOSE, period**2)
    )