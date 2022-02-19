from abc import ABC, abstractmethod
from typing import Iterable, Callable

from .oscillators import Oscillator
from .timeframes import Timeframes
from .broker import Broker
from .timeframes_candle import TimeframesCandle
from .market_data_analyzer import MarketDataAnalyzer
from .candles_providers import CandlesProvider
from .broker.orders import MarketBuy, MarketSell, LimitBuy, LimitSell


class TradingStrategy(ABC):
    """
    Base class for strategies

    Override "using_candles" to define what timeframes will be used
        in strategy and make them available in __call__ method
        via self.candles.get(timeframe)

    Override "using_oscillators" to define what oscillators will be
        used in strategy and make then available in __call__ method
        via self.oscillators.get(oscillator_name)

    Override analyzer_t to provide custom analyzer class
    """
    using_candles: Iterable[Timeframes] = None
    using_oscillators: Iterable[Callable[..., Oscillator]] = None
    analyzer_t = MarketDataAnalyzer

    def __init__(self, market_data: CandlesProvider, broker: Broker):
        self._market_data = market_data
        self._broker = broker

        if self.using_oscillators:
            self._oscillators = self.analyzer_t(
                market_data, self.using_oscillators)
        else:
            self._oscillators = None

        if self.using_candles:
            self._candles = TimeframesCandle(
                market_data, self.using_candles)
        else:
            self._candles = None

    def next(self) -> None:
        """
        Runs each time a new candle closes
        and forwards the call to linked instances
        to keep all data up to date
        """
        self._market_data.next()

        if self._broker.has_orders():
            self._broker.update()
        if self._candles:
            self._candles.update()
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
    def oscillators(self) -> MarketDataAnalyzer:
        return self._oscillators

    @property
    def candles(self) -> TimeframesCandle:
        return self._candles

    @property
    def position(self):
        pos = self._broker.position()
        if not pos.opened():
            return None
        else:
            return pos

    @abstractmethod
    def __call__(self) -> None:
        """ The lands of user code """
        pass
