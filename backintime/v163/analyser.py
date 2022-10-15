import typing as t

from collections import deque
from dataclasses import dataclass
from itertools import islice
from backintime.v163.data.data_provider import Candle
from backintime.v163.oscillators import Oscillator, OscillatorParam
from backintime.v163.timeframes import Timeframes as tf
from backintime.v163.candle_properties import CandleProperties as CandleProps


@dataclass
class OscillatorParam:
    timeframe: tf
    candle_property: CandleProps
    quantity: int
    values: t.Optional[t.List[float]]


class AnalyserBuffer:
    def __init__(self, params: t.Iterable[OscillatorParam], base_timeframe: tf):
        self._base_timeframe=base_timeframe
        self._data = self._prepare(params)

    def _prepare(self, params: t.Iterable[OscillatorParam]) -> dict:
        data = {}
        for param in params:
            if not param.timeframe in data:
                data[param.timeframe] = {
                    param.candle_property : deque(param.quantity)
                }
            else:
                tf_data = data[param.timeframe]
                buffer = tf_data.get(param.candle_property, [])
                tf_data[param.candle_property] = deque(buffer, 
                                                       param.quantity)
        return data

    def get(self, 
            timeframe: tf, 
            candle_property: CandleProps, 
            quantity: int) -> t.List[float]:
        data = self._data[timeframe][candle_property]
        return list(islice(data, 0, min(quantity, data.maxlen)))
        
    def update(self, candle: Candle, ticks: int) -> None:
        for timeframe, tf_data in self._data.items():
            ratio = timeframe.value/self._base_timeframe.value
            remainder = ticks % ratio 
            
            if not remainder:
                # Update all props
                if CandleProps.OPEN in tf_data:
                    tf_data[CandleProps.OPEN].append(candle.open)
                if CandleProps.HIGH in tf_data:
                    tf_data[CandleProps.HIGH].append(candle.high)
                if CandleProps.LOW in tf_data:
                    tf_data[CandleProps.LOW].append(candle.low)
                if CandleProps.CLOSE in tf_data:
                    tf_data[CandleProps.CLOSE].append(candle.close)
                if CandleProps.VOLUME in tf_data:
                    tf_data[CandleProps.VOLUME].append(candle.volume)
            else:
                # Insert new data where needed
                if CandleProps.HIGH in tf_data:
                    highs = tf_data[CandleProps.HIGH]
                    if candle.high > highs[-1]:
                        highs[-1] = candle.high

                if CandleProps.LOW in tf_data:
                    lows = tf_data[CandleProps.LOW]
                    if candle.low < lows[-1]:
                        lows[-1] = candle.low
                    
                if CandleProps.CLOSE in tf_data:
                    closes = tf_data[CandleProps.CLOSE]
                    closes[-1] = candle.close

                if CandleProps.VOLUME in tf_data:
                    volumes = tf_data[CandleProps.VOLUME]
                    volumes[-1] = candle.volume


class Analyser:
    def __init__(self, 
                 oscillators: t.Iterable[Oscillator], 
                 buffer: AnalyserBuffer):
        self._buffer = buffer
        self._oscillators = {
            oscillator.get_name() : oscillator 
                for oscillator in oscillators
        }
    
    def get(self, name: str, timeframe: tf) -> list:
        """ Get list of oscillator values """
        pass

    def get_last(self, name: str, timeframe: tf) -> t.Any:
        """ Get last oscillator value """
        pass
        