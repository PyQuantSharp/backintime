from abc import abstractmethod
from .tick_counter import TickCounter
from ..timeframes import Timeframes
from ..candle import Candle

import datetime


class CandlesProvider:

    def __init__(self, timeframe_tag: Timeframes):
        self._timeframe_tag = timeframe_tag
        self._tick_counter = TickCounter()
        self._candle_buffer = Candle()

    def get_ticks(self) -> int:
        return self._tick_counter.get_ticks()

    def set_start_date(self, since: datetime.datetime) -> None:
        self._start_date = since

    def candle_duration(self) -> int:
        return self._timeframe_tag.value

    def current_candle(self) -> Candle:
        return self._candle_buffer

    @abstractmethod
    def next(self) -> None:
        pass
