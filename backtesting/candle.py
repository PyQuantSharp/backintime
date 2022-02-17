from dataclasses import dataclass
import datetime


@dataclass
class Candle:
    open:     float = None
    high:     float = None
    low:      float = None
    close:    float = None
    volume:   float = None
    is_closed: bool = True
    open_time: datetime.datetime=None
    close_time: datetime.datetime=None
