from typing import Union
from datetime import datetime, timedelta
from ...candle import Candle


def to_ms(time_obj: Union[float, datetime, timedelta]) -> int:
    # timestamp
    if isinstance(time_obj, float):
        return int(time_obj*1000)
    # datetime
    elif isinstance(time_obj, datetime):
        return int(time_obj.timestamp()*1000)
    # timedelta
    elif isinstance(time_obj, timedelta):
        return int(time_obj.total_seconds()*1000)


def _parse_time(millis_timestamp) -> datetime:
    return datetime.utcfromtimestamp(millis_timestamp/1000)


def to_candle(candle_arr, candle_buffer: Candle) -> None:
    candle_buffer.open = float(candle_arr[1])
    candle_buffer.high = float(candle_arr[2])
    candle_buffer.low = float(candle_arr[3])
    candle_buffer.close = float(candle_arr[4])
    candle_buffer.volume = float(candle_arr[5])
    # read timestamp to datetime.datetime
    open_time = _parse_time(candle_arr[0])
    candle_buffer.open_time = open_time
    close_time = _parse_time(candle_arr[6])
    candle_buffer.close_time = close_time
