from .timeframe_dump_scheme import TimeframeDumpScheme
from ..candles_provider import CandlesProvider
from ...timeframes import Timeframes

import pandas as pd
import datetime


class TimeframeDump(CandlesProvider):

    def __init__(
            self,
            filename: str,
            timeframe_tag: Timeframes,
            scheme: TimeframeDumpScheme = TimeframeDumpScheme()
            ):
        # scheme specifies indexes to use for fetching candle' open time and OHLC info
        self._scheme = scheme
        self._data = pd.read_csv(
            filename, sep=';', parse_dates=[scheme.open_time_idx, scheme.close_time_idx]
        )
        self._gen = None
        self._prev_time = None
        super().__init__(timeframe_tag)

    def current_date(self):
        #
        if not self._start_date:
            return None

        ticks = self.get_ticks()
        time_passed = datetime.timedelta(
            seconds=ticks*self.candle_duration()
        )
        return self._start_date + time_passed


    def next(self) -> None:

        if not self._gen:
            self._gen = iter(self._data.iterrows())

        _, row = next(self._gen)

        open_time = row[self._scheme.open_time_idx]

        if self._start_date:
            # skip rows until desired date
            while open_time < self._start_date:
                _, row = next(self._gen)
                open_time = row[self._scheme.open_time_idx]
        # snippet to catch malformed
        # input with time loops
        # for debug mostly
        if self._prev_time:
            while open_time < self._prev_time:
                # skip rows with invalid date
                _, row = next(self._gen)
                open_time = row[self._scheme.open_time_idx]

        self._prev_time = open_time
        # end snippet
        self._candle_buffer.open_time = open_time
        self._candle_buffer.close_time = row[self._scheme.close_time_idx]
        self._candle_buffer.open = row[self._scheme.open_idx]
        self._candle_buffer.high = row[self._scheme.high_idx]
        self._candle_buffer.low = row[self._scheme.low_idx]
        self._candle_buffer.close = row[self._scheme.close_idx]
        self._candle_buffer.volume = row[self._scheme.volume_idx]
        self._tick_counter.increment()
