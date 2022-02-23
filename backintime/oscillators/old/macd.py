from typing import Callable

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import talib


class MacdResults:
    def __init__(self, macd, signal, hist):
        self.macd = macd
        self.signal = signal
        self.hist= hist
    # TODO: add lookup param?
    def crossover_up(self) -> bool:
        if not self.hist[-1]:
            return False
        return self.hist[-1] > 0 and self.hist[-2] <= 0

    def crossover_down(self) -> bool:
        if not self.hist[-1]:
            return False
        return self.hist[-1] <= 0 and self.hist[-2] > 0


class MACD(Oscillator):

    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            fastperiod: int=12,
            slowperiod: int=26,
            signalperiod: int=9
    ):
        name = f'MACD_{timeframe.name}'
        self._fastperiod = fastperiod
        self._slowperiod = slowperiod
        self._signalperiod = signalperiod
        self._reserved_size = 300
        super().__init__(market_data, timeframe, name)

    def reserve(self) -> None:
        self._market_data.reserve(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size
        )

    def __call__(self) -> MacdResults:
        close = self._market_data.get(
            self._timeframe,
            CandleProperties.CLOSE,
            self._reserved_size
        )

        fast_ema = talib.EMA(close, self._fastperiod)
        slow_ema = talib.EMA(close, self._slowperiod)

        macd = fast_ema - slow_ema

        try:
            signal = talib.EMA(macd, self._signalperiod)
            hist = macd - signal
        except Exception as e:
            signal = [None]
            hist = [None]

        return MacdResults(macd, signal, hist)
        '''
        The above could be also calculated with:

        macd, signal, hist = talib.MACD(close, self._fastperiod, self._slowperiod, self._signalperiod)
        but with 33* initial gap
        '''

def macd(
        timeframe: Timeframes,
        fastperiod: int=12,
        slowperiod: int=26,
        signalperiod: int=9) -> Callable:
    #
    return lambda market_data: MACD(
        market_data, timeframe,
        fastperiod, slowperiod, signalperiod
    )
