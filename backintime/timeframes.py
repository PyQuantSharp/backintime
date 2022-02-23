from enum import Enum


class Timeframes(Enum):
    # seconds
    S1 = 1
    S5 = 5
    S15 = 15
    S30 = 30
    # minutes
    M1 = 60
    M3 = 180
    M5 = 300
    M15 = 900
    M30 = 1800
    M45 = 2700
    # hours
    H1 = 3600
    H2 = 7200
    H3 = 10800
    H4 = 14400
    # day
    D1 = 86400
    # week
    W1 = 604800
