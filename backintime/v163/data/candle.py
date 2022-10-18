import typing as t

from datetime import datetime
from dataclasses import dataclass


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float
    open_time: datetime
    close_time: datetime
    is_closed: t.Optional[bool]=True