from ..candles_providers import CandlesProvider
from ..candle_properties import CandleProperties
from ..timeframes import Timeframes
from .timeframe_values import TimeframeValues


class MarketDataStorage:

    def __init__(self, market_data: CandlesProvider):
        self._market_data = market_data
        self._timeframes_values = {}

    def get(self, timeframe: Timeframes, property: CandleProperties, max_size: int):
        timeframe_values = self._timeframes_values[timeframe]
        return timeframe_values.get(property, max_size)

    def reserve(
            self,
            timeframe: Timeframes,
            property: CandleProperties,
            size: int
            ) -> None:

        if not timeframe in self._timeframes_values:
            self._timeframes_values[timeframe] = TimeframeValues(timeframe, self._market_data)

        timeframe_values = self._timeframes_values[timeframe]

        if not property in timeframe_values:
            timeframe_values.add_property_buffer(property, size)

        property_buffer = timeframe_values.get_property_buffer(property)

        if property_buffer.capacity() < size:
            property_buffer.resize(size)

    def update(self) -> None:
        for timeframe_values in self._timeframes_values.values():
            timeframe_values.update()
