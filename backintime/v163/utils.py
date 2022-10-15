from backintime.v163.candle import Candle
from backintime.v163.timeframes import Timeframes


def update_candle(candle: Candle, 
                  candle_timeframe: Timeframes, 
                  new_candle: Candle, 
                  new_candle_timeframe: Timeframes, 
                  ticks: int) -> None:
    ratio = candle_timeframe.value/new_candle_timeframe.value
    remainder = ticks % ratio 
    if not remainder:
        candle.open_time = new_candle.open_time
        candle.open = new_candle.open 
        candle.high = new_candle.high
        candle.low = new_candle.low
        candle.close = new_candle.close
    else:
        candle.high = max(candle.high, new_candle.high)
        candle.low = min(candle.low, new_candle.low)
        candle.close = new_candle.close
    candle.is_closed = (ratio - remainder == 1)