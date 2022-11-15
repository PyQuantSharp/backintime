import typing as t

from abc import ABC, abstractmethod
from backintime.v163.broker import Broker
from backintime.v163.analyser import Analyser
from backintime.v163.candles import Candles
from backintime.v163.oscillators import Oscillator
from backintime.v163.timeframes import Timeframes


class TradingStrategy(ABC):
    timeframes: t.Iterable[Timeframes] = []
    oscillators: t.Iterable[Oscillator] = []

    def __init__(self, 
                 broker: Broker,
                 analyser: Analyser,
                 candles: Candles):
        self._broker=broker
        self._analyser=analyser
        self._candles=candles

    @abstractmethod
    def tick(self) -> None:
        """ The lands of user code """
        # macd = self._analyser.get_last("macd", tf.H4)
        pass