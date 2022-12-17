import typing as t

from abc import ABC, abstractmethod
from .broker.broker import AbstractBroker
from .analyser.analyser import Analyser
from .candles import Candles
from .timeframes import Timeframes
from .analyser.oscillators.base import OscillatorFactory


class TradingStrategy(ABC):
    title = ''
    timeframes: t.Set[Timeframes] = set()
    oscillators: t.Set[OscillatorFactory] = set()

    def __init__(self, 
                 broker: AbstractBroker,
                 analyser: Analyser,
                 candles: Candles):
        self.broker=broker
        self.analyser=analyser
        self.candles=candles

    @classmethod
    def get_title(cls) -> str:
        return cls.title or cls.__name__

    def buy(self) -> OrderInfo:
        """Shortcut for submitting market buy order."""
        pass

    def sell(self) -> OrderInfo:
        """Shortcut for submitting market sell order."""
        pass

    @abstractmethod
    def tick(self) -> None:
        """ The lands of user code """
        # macd = self.analyser.get_last("macd", tf.H4)
        pass