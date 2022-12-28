from enum import Enum


class CandleProperties(Enum):
    OPEN = 'OPEN'
    HIGH = 'HIGH'
    LOW = 'LOW'
    CLOSE = 'CLOSE'
    VOLUME = 'VOLUME'


OPEN = CandleProperties.OPEN
HIGH = CandleProperties.HIGH
LOW = CandleProperties.LOW
CLOSE = CandleProperties.CLOSE
VOLUME = CandleProperties.VOLUME