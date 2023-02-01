import typing as t
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from .data.candle import Candle as InputCandle
from .timeframes import Timeframes, estimate_close_time


@dataclass
class Candle:
    """
    Contains a snapshot of OHLCV data of a candle. 
    The `is_closed` attribute can be used to determine if 
    the data is in its final state (i.e., the candle is closed).
    """
    open_time:  datetime
    close_time: datetime
    open:       Decimal = Decimal('NaN')
    high:       Decimal = Decimal('NaN')
    low:        Decimal = Decimal('NaN')
    close:      Decimal = Decimal('NaN')
    volume:     Decimal = Decimal('NaN')
    is_closed:  bool = False


class CandleNotFound(Exception):
    def __init__(self, timeframe: Timeframes):
        message = f"Candle {timeframe} was not found in buffer."
        super().__init__(message)


def _create_placeholder_candle(open_time: datetime, 
                               timeframe: Timeframes) -> Candle:
    close_time = estimate_close_time(open_time, timeframe)
    return Candle(open_time=open_time, close_time=close_time)


class CandlesBuffer:
    """
    Provides the last candle representation for all timeframes
    passed to ctor.
    It is useful for checking properties of a candle 
    on one timeframe (H1, for example), while having data
    on another (for instance, M1).
    """
    def __init__(self,
                 start_time: datetime,
                 timeframes: t.Set[Timeframes]):
        self._data = {
            timeframe: _create_placeholder_candle(start_time, timeframe)
                for timeframe in timeframes 
        }

    def get(self, timeframe: Timeframes) -> Candle:
        """
        Get the last candle representation on `timeframe`.
        If the candle of `timeframe` is not found, 
        raises `CandleNotFound`.
        """
        try:
            return self._data[timeframe]
        except KeyError:
            raise CandleNotFound(timeframe)

    def update(self, candle: InputCandle) -> None:
        """Update stored candles data in accordance with `candle`."""
        for timeframe in self._data:
            self._update_candle(timeframe, candle) 

    def _update_candle(self, 
                       timeframe: Timeframes, 
                       new_candle: InputCandle) -> None:
        candle = self.get(timeframe)
        if new_candle.close_time > candle.close_time or \
                new_candle.open_time == candle.open_time:
            close_time = estimate_close_time(
                            new_candle.open_time, timeframe)
            candle.open_time = new_candle.open_time
            candle.open = new_candle.open 
            candle.high = new_candle.high
            candle.low = new_candle.low
            candle.close = new_candle.close
            candle.close_time = close_time
            candle.volume = new_candle.volume
        else:
            candle.high = max(candle.high, new_candle.high)
            candle.low = min(candle.low, new_candle.low)
            candle.close = new_candle.close
            candle.volume += new_candle.volume

        candle.is_closed = (new_candle.close_time == candle.close_time)


class Candles:
    """
    Provides the last candle representation for various timeframes.
    It is useful for checking properties of a candle 
    on one timeframe (H1, for example), while having data
    on another (for instance, M1).
    """
    def __init__(self, buffer: CandlesBuffer):
        self._buffer=buffer

    def get(self, timeframe: Timeframes) -> Candle:
        """
        Get the last candle representation on `timeframe`.
        If the candle of `timeframe` is not found, 
        raises `CandleNotFound`.
        """
        return replace(self._buffer.get(timeframe))
