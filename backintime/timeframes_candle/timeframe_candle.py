from ..timeframes import Timeframes
from ..candles_providers import CandlesProvider
from ..candle import Candle

import datetime


def _copy_ohlcv(src: Candle, dst: Candle) -> None:
    dst.open = src.open
    dst.high = src.high
    dst.low = src.low
    dst.close = src.close
    dst.volume = src.volume


class TimeframeCandle:

    def __init__(self, timeframe: Timeframes, market_data: CandlesProvider):
        candle_duration = timeframe.value
        base_candle_duration = market_data.candle_duration()
        self._market_data = market_data
        self._relative_duration = candle_duration // base_candle_duration
        self._candle_duration = datetime.timedelta(seconds=timeframe.value)
        self._candle_buffer = Candle()

    def current_candle(self) -> Candle:
        return self._candle_buffer

    def update(self) -> None:
        candle = self._market_data.current_candle()
        ticks = self._market_data.get_ticks()

        q, r = divmod(ticks, self._relative_duration)

        self._candle_buffer.is_closed = r == 0

        if self._relative_duration == 1 or r == 1:
            # Полная перезапись свечки
            _copy_ohlcv(candle, self._candle_buffer)
            self._candle_buffer.open_time = candle.open_time
            self._candle_buffer.close_time = candle.open_time + self._candle_duration

        else:
            # А тут только сравнением
            self._candle_buffer.close = candle.close
            self._candle_buffer.volume += candle.volume

            if candle.high > self._candle_buffer.high:
                self._candle_buffer.high = candle.high

            if candle.low < self._candle_buffer.low:
                self._candle_buffer.low = candle.low
        # rel == 1 --> полная перезапись, is_closed <- True
        # R == 1 --> полная перезапись, is_closed <- False
        # R == 0 --> is_closed <- True
