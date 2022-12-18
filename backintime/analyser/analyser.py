import typing as t

from collections import deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from itertools import islice
from backintime.timeframes import Timeframes, estimate_close_time
from .oscillators.constants import CandleProperties
from .oscillators.base import (
    Oscillator, 
    OscillatorFactory, 
    OscillatorResultSequence, 
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
                   quantity: int) -> list:
        data = self._data[timeframe][candle_property]
        return list(islice(data, data.maxlen - quantity, data.maxlen))

    def update(self, candle) -> None:
        for timeframe, series in self._data.items():
            if candle.close_time > series['end_time']:
                # Push new values
                close_time = estimate_close_time(
                                candle.open_time, timeframe)
                series['end_time'] = close_time
                if CandleProperties.OPEN in series:
                    series[CandleProperties.OPEN].append(candle.open)
                if CandleProperties.HIGH in series:
                    series[CandleProperties.HIGH].append(candle.high)
                if CandleProperties.LOW in series:
                    series[CandleProperties.LOW].append(candle.low)
                if CandleProperties.CLOSE in series:
                    series[CandleProperties.CLOSE].append(candle.close)
                if CandleProperties.VOLUME in series:
                    series[CandleProperties.VOLUME].append(candle.volume)
            else:
                # Only update last values if needed
                if CandleProperties.HIGH in series:
                    highs = series[CandleProperties.HIGH]
                    if candle.high > highs[-1]:
                        highs[-1] = candle.high

                if CandleProperties.LOW in series:
                    lows = series[CandleProperties.LOW]
                    if candle.low < lows[-1]:
                        lows[-1] = candle.low
                    
                if CandleProperties.CLOSE in series:
                    closes = series[CandleProperties.CLOSE]
                    closes[-1] = candle.close

                if CandleProperties.VOLUME in series:
                    volumes = series[CandleProperties.VOLUME]
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


class OscillatorNotFound(Exception):
    def __init__(self, oscillator_name: str):
        super().__init__(f"Oscillator {oscillator_name} was not found")


class Analyser:
    def __init__(self,
                 buffer: AnalyserBuffer,
                 oscillator_factories: t.Set[OscillatorFactory]):
        market_data = MarketDataInfo(buffer)
        self._oscillators: t.Dict[str, Oscillator] = {
            factory.get_oscillator_name() : factory.create(market_data) 
                for factory in oscillator_factories
        }

    def get(self, oscillator_name: str) -> OscillatorResultSequence:
        """Get a list of oscillator values."""
        oscillator = self._oscillators.get(oscillator_name)
        if not oscillator:
            raise OscillatorNotFound(oscillator_name)
        return oscillator()

    def get_last(self, oscillator_name: str) -> t.Any:
        """Get the last oscillator value."""
        oscillator = self._oscillators.get(oscillator_name)
        if not oscillator:
            raise OscillatorNotFound(oscillator_name)
        return oscillator()[-1]
