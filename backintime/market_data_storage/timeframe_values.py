from typing import Iterable, TypeVar, Generator
from itertools import islice

from ..timeframes import Timeframes
from ..candles_providers import CandlesProvider
from ..candle_properties import CandleProperties
from .property_buffer import PropertyBuffer
from .float_generator import FloatGenerator


class TimeframeValues:

    def __init__(self, timeframe: Timeframes, market_data: CandlesProvider):
        candle_duration = timeframe.value
        base_candle_duration = market_data.candle_duration()
        self._relative_duration = candle_duration // base_candle_duration
        self._property_buffers = {}
        self._market_data = market_data

    def get(
            self,
            property: CandleProperties,
            max_size: int
    ) -> FloatGenerator:

        data = self._property_buffers[property]
        items_count = len(data)
        # values with idx from 0 to specified size
        return islice(data.values(), 0, min(max_size, items_count))

    def get_property_buffer(self, property: CandleProperties):
        return self._property_buffers[property]

    def add_property_buffer(self, property: CandleProperties, size: int):
        self._property_buffers[property] = PropertyBuffer(size)

    def get_properties(self) -> Iterable[CandleProperties]:
        return self._property_buffers.keys()

    def __contains__(self, property: CandleProperties) -> bool:
        return property in self._property_buffers

    def update(self) -> None:
        candle = self._market_data.current_candle()
        ticks = self._market_data.get_ticks()
        properties = self.get_properties()

        q, r = divmod(ticks, self._relative_duration)

        if self._relative_duration == 1 or r == 1:
            # добавляем новые значения в буффер
            if CandleProperties.OPEN in properties:
                self._property_buffers[CandleProperties.OPEN].append(candle.open)

            if CandleProperties.HIGH in properties:
                self._property_buffers[CandleProperties.HIGH].append(candle.high)

            if CandleProperties.LOW in properties:
                self._property_buffers[CandleProperties.LOW].append(candle.low)

            if CandleProperties.CLOSE in properties:
                self._property_buffers[CandleProperties.CLOSE].append(candle.close)

            if CandleProperties.VOLUME in properties:
                self._property_buffers[CandleProperties.VOLUME].append(candle.volume)

        else:
            # по необходимости редактируем последнюю свечку в буфере
            if CandleProperties.CLOSE in properties:
                buffer = self._property_buffers[CandleProperties.CLOSE]
                buffer.pop()
                buffer.append(candle.close)

            if CandleProperties.HIGH in properties:
                buffer = self._property_buffers[CandleProperties.HIGH]
                stored_high = buffer.pop()
                if candle.high > stored_high:
                    stored_high = candle.high
                buffer.append(stored_high)

            if CandleProperties.LOW in properties:
                buffer = self._property_buffers[CandleProperties.LOW]
                stored_low = buffer.pop()
                if candle.low < stored_low:
                    stored_low = candle.low
                buffer.append(stored_low)

            if CandleProperties.VOLUME in properties:
                buffer = self._property_buffers[CandleProperties.VOLUME]
                stored_volume = buffer.pop()
                buffer.append(stored_volume + candle.volume)
