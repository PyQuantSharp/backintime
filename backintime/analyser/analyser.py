import typing as t

from collections import deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from itertools import islice
from backintime.timeframes import Timeframes, estimate_close_time
from .indicators.constants import (
    CandleProperties, 
    OPEN, 
    HIGH, 
    LOW, 
    CLOSE,
    VOLUME
)
from .indicators.base import (
    Indicator, 
    IndicatorFactory, 
    ResultSequence, 
    MarketData
)


class AnalyserBuffer:
    def __init__(self, start_time: datetime):
        self._start_time = start_time
        self._data: t.Dict[Timeframes, t.Dict] = {}

    def reserve(self, 
                timeframe: Timeframes, 
                candle_property: CandleProperties,
                quantity: int) -> None:
        """
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
                   limit: int) -> list:
        """
        Get at most `limit` values of `candle_property` 
        for `timeframe`.
        """
        data = self._data[timeframe][candle_property]
        offset = max(0, data.maxlen - limit)
        return list(islice(data, offset, data.maxlen))

    def update(self, candle) -> None:
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
                   quantity: int) -> list:
        return self._data.get_values(timeframe, candle_property, quantity)


class IndicatorNotFound(Exception):
    def __init__(self, indicator_name: str):
        super().__init__(f"Indicator {indicator_name} was not found")


class Analyser:
    def __init__(self,
                 buffer: AnalyserBuffer,
                 indicator_factories: t.Set[IndicatorFactory]):
        market_data = MarketDataInfo(buffer)
        self._indicators: t.Dict[str, Indicator] = {
            factory.indicator_name : factory.create(market_data) 
                for factory in indicator_factories
        }

    def get(self, indicator_name: str) -> ResultSequence:
        """Get sequence of indicator values."""
        indicator = self._indicators.get(indicator_name)
        if not indicator:
            raise IndicatorNotFound(indicator_name)
        return indicator()

    def get_last(self, indicator_name: str) -> t.Any:
        """Get the last indicator value."""
        indicator = self._indicators.get(indicator_name)
        if not indicator:
            raise IndicatorNotFound(indicator_name)
        return indicator()[-1]
