from typing import Any  # to fix Order circular import
from dataclasses import dataclass
import datetime


@dataclass
class Trade:
    """ Trade represents executed order """
    time_1: datetime.datetime
    time_2: datetime.datetime
    order: Any  # expecting Order
    profit: float
    fee: float
