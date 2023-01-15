import ta
import numpy
import pandas as pd
import typing as t
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CLOSE
from .base import MarketData, IndicatorParam


def rsi(market_data: MarketData, timeframe: Timeframes,
            period: int = 14) -> numpy.ndarray:
    quantity = period**2
    close = market_data.get_values(timeframe, CLOSE, quantity)
    close = pd.Series(close)
    rsi = ta.momentum.RSIIndicator(close, period).rsi()
    return rsi.values


def rsi_params(timeframe: Timeframes,
               period: int = 14) -> t.Tuple[IndicatorParam]:
    """Get list of RSI params."""
    return (
        IndicatorParam(timeframe=timeframe, 
                       candle_property=CLOSE,
                       quantity=period**2),
    )