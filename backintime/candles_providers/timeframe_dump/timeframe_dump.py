from .timeframe_dump_scheme import TimeframeDumpScheme
from .utils import to_candle
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
            filename,
            sep=';',
            parse_dates=[scheme.open_time_idx, scheme.close_time_idx]
        )
        self._gen = None
        super().__init__(timeframe_tag)

    def current_date(self):
        if not self._start_date:
            return None
        ticks = self.get_ticks()
        time_passed = datetime.timedelta(
            seconds=ticks*self.candle_duration())
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

        self._candle_buffer.open_time = open_time
        to_candle(row, scheme, self._candle_buffer)
        self._tick_counter.increment()
