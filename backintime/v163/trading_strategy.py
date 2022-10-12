import typing as t

from abc import ABC, abstractmethod
from backintime.v163.broker import Broker


class TradingStrategy(ABC):
    timeframes: t.Iterable[Timeframes] = None
    oscillators: t.Iterable[t.Callable[..., Oscillator]] = None

    def __init__(self, broker: Broker):
        self._broker = broker

    @property
    def oscillators(self) -> MarketDataAnalyzer:
        return self._oscillators

    @property
    def candles(self) -> TimeframesCandle:
        return self._candles

    @abstractmethod
    def tick(self, candle) -> None:
        """ The lands of user code """
        macd = self.oscillators.update(candle).get("macd", tf.H4)
