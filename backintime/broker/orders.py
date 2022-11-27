"""
Orders only hold required data, but the desired functions 
must be implemented somewhere else. 
All fields are public. It is up to a broker implementation to set 
`status` and provide TP/SL orders features:

    - Multiple TP/SL orders can be posted for the same position, 
      so the summarised value of opened TP/SL orders can be greater
      than the opened position. 
      In this case, only the first TP/SL order whose conditions
      are satisafied will be executed. Others must be cancelled.

    - When TP/SL order is activated (target_price meets market), 
      it must be treated as Market/Limit order,
      depending on whether `order_price` was provided.
"""
import typing as t
from abc import ABC, abstractmethod
from enum import Enum


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    CREATED = "CREATED"
    CANCELLED = "CANCELLED"
    EXECUTED = "EXECUTED"
    # Only for stop loss orders
    ACTIVATED = "ACTIVATED"


class Order:
    """ Base class for all orders """
    def __init__(self, 
                 side: OrderSide, 
                 amount: float, 
                 order_price: t.Optional[float]=None):
        self.side = side
        self.amount = amount
        self.order_price = order_price
        self.fill_price: t.Optional[float] = None
        self.status = OrderStatus.CREATED

# Strategy orders have trigger price
class StrategyOrder(Order):
    def __init__(self,
                 side: OrderSide, 
                 amount: float, 
                 trigger_price: float,
                 order_price: t.Optional[float]=None):
        self.trigger_price = trigger_price
        super().__init__(side, amount, order_price)


class TakeProfitOrder(StrategyOrder): pass


class StopLossOrder(StrategyOrder): pass


class OrderFactory(ABC):
    @abstractmethod
    def create(self) -> Order:
        pass


class TakeProfitFactory(OrderFactory):
    def __init__(self, 
                 amount: float, 
                 trigger_price: float, 
                 order_price: t.Optional[float]=None):
        self.amount = amount
        self.trigger_price = trigger_price
        self.order_price = order_price
        self.side: t.Optional[OrderSide] = None  # Shouldn't be set by user

    def create(self) -> TakeProfitOrder:
        return TakeProfitOrder(self.side, self.amount, 
                               self.trigger_price, self.order_price)


class StopLossFactory(OrderFactory):
    def __init__(self, 
                 amount: float, 
                 trigger_price: float, 
                 order_price: t.Optional[float]=None):
        self.amount = amount
        self.trigger_price = trigger_price
        self.order_price = order_price
        self.side: t.Optional[OrderSide] = None # Shouldn't be set by user

    def create(self) -> StopLossOrder:
        return StopLossOrder(self.side, self.amount, 
                             self.trigger_price, self.order_price)


class MarketOrder(Order):
    def __init__(self, side: OrderSide, amount: float):
        super().__init__(side, amount)

# Limit orders have optional TP/SL
class LimitOrder(Order):
    def __init__(self, 
                 side: OrderSide,
                 amount: float,
                 order_price: float,
                 take_profit_factory: t.Optional[TakeProfitFactory] = None,
                 stop_loss_factory: t.Optional[StopLossFactory] = None):
        # TODO: consider collections instead of single item
        self.take_profit_factory = take_profit_factory
        self.stop_loss_factory = stop_loss_factory
        self.take_profit: t.Optional[TakeProfitOrder] = None 
        self.stop_loss: t.Optional[StopLossOrder] = None
        super().__init__(side, amount, order_price)


class MarketOrderFactory(OrderFactory):
    def __init__(self, side: OrderStatus, amount: float):
        self.side = side
        self.amount = amount

    def create(self) -> MarketOrder:
        return MarketOrder(self.side, self.amount)


class LimitOrderFactory(OrderFactory):
    def __init__(self, 
                 side: OrderSide,
                 amount: float, 
                 order_price: float, 
                 take_profit_factory: t.Optional[TakeProfitFactory] = None,
                 stop_loss_factory: t.Optional[StopLossFactory] = None):
        self.side = side
        self.amount = amount
        self.order_price = order_price
        self.take_profit_factory = take_profit_factory
        self.stop_loss_factory = stop_loss_factory

    def create(self) -> LimitOrder:
        return LimitOrder(self.side, self.amount, self.order_price,
                          self.take_profit_factory, self.stop_loss_factory)
