import ta
import numpy
import pandas as pd
import typing as t
from backintime.timeframes import Timeframes
from .constants import CandleProperties, CLOSE
from .base import MarketData, IndicatorParam


def ema(market_data: MarketData, timeframe: Timeframes,
            candle_property: CandleProperties = CLOSE,
            period: int = 9) -> numpy.ndarray:
    """Exponential Moving Average (EMA)."""
    quantity = period**2
    values = market_data.get_values(timeframe, candle_property, quantity)
    values = pd.Series(values)
    ema = ta.trend.EMAIndicator(values, period).ema_indicator()
    return ema.values


def ema_params(timeframe: Timeframes, 
               candle_property: CandleProperties = CLOSE,
               period: int = 9) -> t.Tuple[IndicatorParam]:
    """Get list of EMA params."""
    return (
        IndicatorParam(timeframe=timeframe, 
                       candle_property=candle_property, 
                       quantity=period**2),
    )