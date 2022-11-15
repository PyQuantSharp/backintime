from datetime import datetime
from dataclasses import dataclass
from backintime.v163.data.data_provider import Candle


def to_ms(time: datetime) -> int:
    """ Convert `datetime` to milliseconds timestamp """
    return int(time.timestamp()*1000)

def parse_time(millis_timestamp: int) -> datetime:
    """ Convert milliseconds timestamp to `datetime` """
    return datetime.utcfromtimestamp(millis_timestamp/1000)

def parse_candle(candle: list) -> Candle:
    return Candle(open_time=parse_time(candle[0]),
                  open=float(candle[1]),
                  high=float(candle[2]),
                  low=float(candle[3]),
                  close=float(candle[4]),
                  volume=float(candle[5]),
                  close_time=parse_time(candle[6]))