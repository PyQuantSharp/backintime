from typing import Iterable

from ..candle import Candle
from ..candles_providers import CandlesProvider
from ..timeframes import Timeframes
from .timeframe_candle import TimeframeCandle


class TimeframesCandle:
    """
    Represents the last candle read from the feed
    in all timeframes provided to constructor.
    """
    def __init__(
            self,
            market_data: CandlesProvider,
            using_timeframes: Iterable[Timeframes]
            ):
        '''
        Доп требование - все тф должны быть <= market_data.timeframe
        && тф // market_data.timeframe без остатка
        '''
        self._timeframes_data = {
            timeframe : TimeframeCandle(timeframe, market_data)
                for timeframe in using_timeframes
        }

    def get(self, timeframe: Timeframes) -> Candle:
        return self._timeframes_data[timeframe].current_candle()

    def update(self) -> None:
        for timeframe_data in self._timeframes_data.values():
            timeframe_data.update()
