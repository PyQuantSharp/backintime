from .timeframe_dump_scheme import TimeframeDumpScheme
from ...candle import Candle


def to_candle(arr, scheme: TimeframeDumpScheme, dst: Candle) -> None:
    dst.close_time = row[self._scheme.close_time_idx]
    dst.open = row[self._scheme.open_idx]
    dst.high = row[self._scheme.high_idx]
    dst.low = row[self._scheme.low_idx]
    dst.close = row[self._scheme.close_idx]
    dst.volume = row[self._scheme.volume_idx]
