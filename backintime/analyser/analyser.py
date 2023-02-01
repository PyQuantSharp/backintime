import numpy
import typing as t
from decimal import Decimal
from collections import deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from itertools import islice
from backintime.timeframes import Timeframes, estimate_close_time

from .indicators.base import MarketData
from .indicators.adx import adx
from .indicators.atr import atr
from .indicators.bbands import bbands, BbandsResultSequence
from .indicators.dmi import dmi, DMIResultSequence
from .indicators.ema import ema
from .indicators.macd import macd, MacdResultSequence
from .indicators.rsi import rsi
from .indicators.sma import sma
from .indicators.pivot import (
    pivot,
    pivot_fib,
    pivot_classic,
    TraditionalPivotPoints, 
    FibonacciPivotPoints,
    ClassicPivotPoints
)
from .indicators.constants import (
    CandleProperties, 
    OPEN, 
    HIGH, 
    LOW, 
    CLOSE,
    VOLUME
)



class AnalyserBuffer:
    """Stores market data in a ring-buffer-like structures."""
    def __init__(self, start_time: datetime):
        self._start_time = start_time
        self._data: t.Dict[Timeframes, t.Dict] = {}

    def reserve(self, 
                timeframe: Timeframes, 
                candle_property: CandleProperties,
                quantity: int) -> None:
        """
        Reserve space in a buffer for `quantity` values
        of `candle_property` on `timeframe`.

        Won't take effect if candle property for the same `timeframe`
        has already been reserved with quantity >= `quantity`.
        """
        tf_data = self._data.get(timeframe)
        if tf_data:
            if not candle_property in tf_data:
                # Add buffer for candle property
                tf_data[candle_property] = deque(maxlen=quantity)
            elif tf_data[candle_property].maxlen < quantity:
                # Resize buffer
                old = tf_data[candle_property]
                tf_data[candle_property] = deque(iter(old), quantity)
        else:   # Make new dict
            self._data[timeframe] = {
                candle_property: deque(maxlen=quantity),
                'end_time': self._start_time
            }

    def get_values(self, 
                   timeframe: Timeframes, 
                   candle_property: CandleProperties,
                   limit: int) -> t.List[Decimal]:
        """
        Get at most `limit` values of `candle_property` 
        for `timeframe`.
        """
        data = self._data[timeframe][candle_property]
        offset = max(0, data.maxlen - limit)
        return list(islice(data, offset, data.maxlen))

    def update(self, candle) -> None:
        """Update stored values in accordance with `candle`."""
        for timeframe, series in self._data.items():
            if candle.close_time > series['end_time']:
                # Push new values
                close_time = estimate_close_time(
                                candle.open_time, timeframe)
                series['end_time'] = close_time
                if OPEN in series:
                    series[OPEN].append(candle.open)
                if HIGH in series:
                    series[HIGH].append(candle.high)
                if LOW in series:
                    series[LOW].append(candle.low)
                if CLOSE in series:
                    series[CLOSE].append(candle.close)
                if VOLUME in series:
                    series[VOLUME].append(candle.volume)
            else:
                # Only update last values if needed
                if HIGH in series:
                    highs = series[HIGH]
                    if candle.high > highs[-1]:
                        highs[-1] = candle.high

                if LOW in series:
                    lows = series[LOW]
                    if candle.low < lows[-1]:
                        lows[-1] = candle.low

                if CLOSE in series:
                    closes = series[CLOSE]
                    closes[-1] = candle.close

                if VOLUME in series:
                    volumes = series[VOLUME]
                    volumes[-1] += candle.volume


class MarketDataInfo(MarketData):
    """
    Wrapper around `AnalyserBuffer` that provides a read-only
    view into the buffered market data series.
    """
    def __init__(self, data: AnalyserBuffer):
        self._data = data

    def get_values(self, 
                   timeframe: Timeframes, 
                   candle_property: CandleProperties, 
                   limit: int) -> t.Sequence[Decimal]:
        return self._data.get_values(timeframe, candle_property, limit)


class Analyser:
    """Indicators calculation."""
    def __init__(self, buffer: AnalyserBuffer):
        self._market_data = MarketDataInfo(buffer)

    def sma(self, 
            timeframe: Timeframes,
            candle_property: CandleProperties = CLOSE,
            period: int = 9) -> numpy.ndarray:
        """Simple Moving Average, also known as 'MA'."""
        return sma(self._market_data, timeframe, candle_property, period)

    def ema(self, 
            timeframe: Timeframes,
            candle_property: CandleProperties = CLOSE,
            period: int = 9) -> numpy.ndarray:
        """Exponential Moving Average (EMA)."""
        return ema(self._market_data, timeframe, candle_property, period)

    def adx(self, timeframe: Timeframes, period: int = 14) -> numpy.ndarray:
        """
        Average Directional Movement Index (ADX).

        ADX does not indicate trend direction or momentum, 
        only trend strength. 
        Generally, ADX readings below 20 indicate trend weakness,
        and readings above 40 indicate trend strength. 
        An extremely strong trend is indicated by readings above 50.
        """
        return adx(self._market_data, timeframe, period)

    def atr(self, timeframe: Timeframes, period: int = 14) -> numpy.ndarray:
        """Average True Range (ATR)."""
        return atr(self._market_data, timeframe, period)

    def rsi(self, timeframe: Timeframes, period: int = 14) -> numpy.ndarray:
        """
        Relative Strength Index (RSI).

        Momentum oscillator that measures the speed and change 
        of price movements. RSI oscillates between zero and 100. 
        Traditionally, and according to Wilder, RSI is considered 
        overbought when above 70 and oversold when below 30.
        """
        return rsi(self._market_data, timeframe, period)

    def bbands(self, 
               timeframe: Timeframes,
               candle_property: CandleProperties = CLOSE,
               period: int = 20,
               deviation_quotient: int = 2) -> BbandsResultSequence:
        """
        Bollinger Bands (BBANDS).

        Bollinger Bands are volatility bands placed above 
        and below a moving average.
        Volatility is based on the standard deviation, 
        which changes as volatility increases and decreases.
        The bands automatically widen when volatility increases
        and narrow when volatility decreases.
        """
        return bbands(self._market_data, timeframe, 
                      candle_property, period, deviation_quotient)

    def dmi(self, timeframe: Timeframes,
                period: int = 14) -> DMIResultSequence:
        """Directional Movement Indicator (DMI)."""
        return dmi(self._market_data, timeframe, period)

    def macd(self, 
             timeframe: Timeframes,
             fastperiod: int = 12,
             slowperiod: int = 26,
             signalperiod: int = 9) -> MacdResultSequence:
        """
        Moving Average Convergence Divergence (MACD).

        Trend-following momentum indicator that shows the 
        relationship between two moving averages of prices.
        """
        return macd(self._market_data, 
                    timeframe, fastperiod, slowperiod, signalperiod)

    def pivot(self, 
              timeframe: Timeframes,
              period: int = 15) -> TraditionalPivotPoints:
        """
        Tradtional Pivot Points.
        https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/

        Represents significant support and resistance levels 
        that can be used to determine potential trades.
        The pivot points come as a technical analysis indicator
        calculated using a security’s high, low, and close.
        """
        return pivot(self._market_data, timeframe, period)

    def pivot_fib(self, 
                  timeframe: Timeframes,
                  period: int = 15) -> FibonacciPivotPoints:
        """
        Fibonacci Pivot Points.
        https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/

        Represents significant support and resistance levels 
        that can be used to determine potential trades.
        The pivot points come as a technical analysis indicator
        calculated using a security’s high, low, and close.
        """
        return pivot_fib(self._market_data, timeframe, period)

    def pivot_classic(self, 
                      timeframe: Timeframes,
                      period: int = 15) -> ClassicPivotPoints:
        """
        Classic Pivot Points.
        https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/

        Represents significant support and resistance levels 
        that can be used to determine potential trades.
        The pivot points come as a technical analysis indicator
        calculated using a security’s high, low, and close.
        """
        return pivot_classic(self._market_data, timeframe, period)