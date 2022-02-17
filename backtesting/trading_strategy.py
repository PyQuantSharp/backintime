from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from .oscillators import Oscillator
from .timeframes import Timeframes
from .broker import Broker
from .timeframes_candle import TimeframesCandle
from .market_data_analyzer import MarketDataAnalyzer
from .candles_providers import CandlesProvider
from .broker.orders import MarketBuy, MarketSell, LimitBuy, LimitSell


class TradingStrategy(ABC):

    using_candles: Tuple[Timeframes] = None
    analyzer_t = MarketDataAnalyzer

    def __init__(self, market_data: CandlesProvider, broker: Broker):
        self._market_data = market_data
        self._broker = broker
        self._oscillators = self.analyzer_t(market_data)

        if self.using_candles:
            self._timeframes_candle = TimeframesCandle(
                market_data, self.using_candles)
        else:
            self._timeframes_candle = None

    def next(self) -> None:
        self._market_data.next()

        if self._broker.has_orders():
            self._broker.update()
        if self._timeframes_candle:
            self._timeframes_candle.update()
        if self._oscillators:
            self._oscillators.update()

        self.__call__()

    def _buy(self, price: float=None, quantity: float=None) -> None:
        order = MarketBuy(quantity) if not price \
            else LimitBuy(price, quantity)
        self._broker.submit(order)

    def _sell(self, price: float=None, quantity: float=None) -> None:
        order = MarketSell(quantity) if not price \
            else LimitSell(price, quantity)
        self._broker.submit(order)

    @property
    def position(self):
        pos = self._broker.position()
        if not pos.opened():
            return None
        else:
            return pos

    @abstractmethod
    def __call__(self) -> None:
        # the lands of user code
        pass
