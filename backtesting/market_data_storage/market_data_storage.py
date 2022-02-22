from ..candles_providers import CandlesProvider
from ..candle_properties import CandleProperties
from ..timeframes import Timeframes
from .timeframe_values import TimeframeValues
from .float_generator import FloatGenerator


class MarketDataStorage:
    """
    Stores historical market data that was reserved by oscillators
    It can be accessed by providing desired timeframe, property and size
    """
    def __init__(self, market_data: CandlesProvider):
        self._market_data = market_data
        self._timeframes_values = {}

    def get(
            self,
            timeframe: Timeframes,
            property: CandleProperties,
            max_size: int
    ) -> FloatGenerator:
        """
        Return at most `max_size` of `property` values
        of `timeframe` candles

        :param timeframe:
            buffer will be associated with this timeframe
        :param property:
            OHLCV property to store
        :param size:
            max size of buffer
        """
        timeframe_values = self._timeframes_values[timeframe]
        return timeframe_values.get(property, max_size)

    def reserve(
            self,
            timeframe: Timeframes,
            property: CandleProperties,
            size: int
    ) -> None:
        """
        Reserves buffer to store at most `size` of `property` values
        of `timeframe` candles
        If already has one, will be resized if needed

        :param timeframe:
            buffer will be associated with this timeframe
        :param property:
            OHLCV property to store
        :param size:
            max size of buffer
        """
        if not timeframe in self._timeframes_values:
            self._timeframes_values[timeframe] = TimeframeValues(timeframe, self._market_data)

        timeframe_values = self._timeframes_values[timeframe]

        if not property in timeframe_values:
            timeframe_values.add_property_buffer(property, size)

        property_buffer = timeframe_values.get_property_buffer(property)

        if property_buffer.capacity() < size:
            property_buffer.resize(size)

    def update(self) -> None:
        """
        Runs each time a new candle closes
        Each value buffer will be updated by the new candle if needed
        """
        for timeframe_values in self._timeframes_values.values():
            timeframe_values.update()
