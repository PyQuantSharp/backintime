import typing as t

from abc import ABC, abstractmethod
from decimal import Decimal
from .candles import Candles
from .timeframes import Timeframes
from .analyser.analyser import Analyser
from .analyser.indicators.base import IndicatorParam
from .broker_proxy import BrokerProxy, OrderInfo, LimitOrderInfo
from .broker.base import (
    OrderSide,
    MarketOrderFactory,
    LimitOrderFactory,
    TakeProfitFactory,
    StopLossFactory
)


class TradingStrategy(ABC):
    title = ''
    indicators: t.Set[t.Tuple[IndicatorParam]] = set()
    candle_timeframes: t.Set[Timeframes] = set()

    def __init__(self, 
                 broker: BrokerProxy,
                 analyser: Analyser,
                 candles: Candles):
        self.broker=broker
        self.analyser=analyser
        self.candles=candles

    @classmethod
    def get_title(cls) -> str:
        return cls.title or cls.__name__

    @property
    def position(self) -> Decimal:
        return self.broker.balance.available_crypto_balance

    def buy(self, amount: t.Optional[Decimal] = None) -> OrderInfo:
        """Shortcut for submitting market buy order."""
        order_amount = amount or self.broker.max_fiat_for_taker
        order = MarketOrderFactory(OrderSide.BUY, order_amount)
        return self.broker.submit_market_order(order)

    def sell(self, amount: t.Optional[Decimal] = None) -> OrderInfo:
        """Shortcut for submitting market sell order."""
        order_amount = amount or self.position
        order = MarketOrderFactory(OrderSide.SELL, order_amount)
        return self.broker.submit_market_order(order)

    def limit_buy(self, 
                  order_price: Decimal,
                  take_profit_factory: t.Optional[TakeProfitFactory] = None,
                  stop_loss_factory: t.Optional[StopLossFactory] = None,
                  amount: t.Optional[Decimal] = None) -> LimitOrderInfo:
        """Shortcut for submitting limit buy order."""
        order_amount = amount or self.broker.max_fiat_for_maker
        order = LimitOrderFactory(OrderSide.BUY,
                                  order_amount,
                                  order_price,
                                  take_profit_factory,
                                  stop_loss_factory)
        return self.broker.submit_limit_order(order)

    def limit_sell(self, 
                   order_price: Decimal,
                   take_profit_factory: t.Optional[TakeProfitFactory] = None,
                   stop_loss_factory: t.Optional[StopLossFactory] = None,
                   amount: t.Optional[Decimal] = None) -> LimitOrderInfo:
        """Shortcut for submitting limit sell order."""
        order_amount = amount or self.position
        order = LimitOrderFactory(OrderSide.SELL,
                                  order_amount,
                                  order_price,
                                  take_profit_factory,
                                  stop_loss_factory)
        return self.broker.submit_limit_order(order)

    @abstractmethod
    def tick(self) -> None:
        """The lands of user code. Runs each time a new candle closes."""
        pass