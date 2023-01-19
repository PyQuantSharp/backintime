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
    """
    Relative Strength Index (RSI).

    Momentum oscillator that measures the speed and change 
    of price movements. RSI oscillates between zero and 100. 
    Traditionally, and according to Wilder, RSI is considered 
    overbought when above 70 and oversold when below 30.
    """
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