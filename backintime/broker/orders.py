"""
Orders only hold required data, but the desired functions 
must be implemented somewhere else. 
All fields are public. It is up to a broker implementation to set 
`status` and provide TP/SL orders features:

    - Multiple TP/SL orders can be posted for the same position, 
      so the summarised value of opened TP/SL orders can be greater
      than the opened position. 
      In this case, only the first TP/SL order whose conditions
      are satisfied will be executed. Others must be cancelled.

    - When TP/SL order is activated (target_price meets market), 
      it must be treated as Market/Limit order,
      depending on whether `order_price` was provided.
"""
import typing as t
from abc import ABC, abstractmethod
from enum import Enum
from decimal import Decimal   # https://docs.python.org/3/library/decimal.html


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self) -> str:
        return self.value


class OrderStatus(Enum):
    CREATED = "CREATED"
    CANCELLED = "CANCELLED"
    EXECUTED = "EXECUTED"
    # Only for stop loss orders
    ACTIVATED = "ACTIVATED"
    
    def __str__(self) -> str:
        return self.value


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"

    def __str__(self) -> str:
        return self.value


class Order:
    """ Base class for all orders """
    def __init__(self, 
                 side: OrderSide,
                 order_type: OrderType,
                 amount: Decimal, 
                 order_price: t.Optional[Decimal]=None):
        self.side = side
        self.order_type = order_type
        self.amount = amount
        self.order_price = order_price
        self.fill_price: t.Optional[Decimal] = None
        self.status = OrderStatus.CREATED

# Strategy orders have trigger price
class StrategyOrder(Order):
    def __init__(self,
                 side: OrderSide, 
                 order_type: OrderType,
                 amount: Decimal, 
                 trigger_price: Decimal,
                 order_price: t.Optional[Decimal]=None):
        self.trigger_price = trigger_price
        super().__init__(side, order_type, amount, order_price)


class TakeProfitOrder(StrategyOrder):
    def __init__(self, 
                 side: OrderSide,
                 amount: Decimal,
                 trigger_price: Decimal,
                 order_price: t.Optional[Decimal]=None):
        order_type = OrderType.TAKE_PROFIT_LIMIT if order_price \
                        else OrderType.TAKE_PROFIT
        super().__init__(self, side, order_type
                         trigger_price, order_price)


class StopLossOrder(StrategyOrder):
    def __init__(self,
                 side: OrderSide,
                 amount: Decimal,
                 trigger_price: Decimal,
                 order_price: t.Optional[Decimal]=None):
        order_type = OrderType.STOP_LOSS_LIMIT if order_price \
                        else OrderType.STOP_LOSS
        super().__init__(side, order_type, amount, 
                         trigger_price, order_price)


class OrderFactory(ABC):
    @abstractmethod
    def create(self) -> Order:
        pass


class TakeProfitFactory(OrderFactory):
    def __init__(self, 
                 amount: Decimal, 
                 trigger_price: Decimal, 
                 order_price: t.Optional[Decimal]=None):
        self.amount = amount
        self.trigger_price = trigger_price
        self.order_price = order_price
        self.side: t.Optional[OrderSide] = None  # Shouldn't be set by user

    def create(self) -> TakeProfitOrder:
        return TakeProfitOrder(self.side, self.amount, 
                               self.trigger_price, self.order_price)


class StopLossFactory(OrderFactory):
    def __init__(self, 
                 amount: Decimal, 
                 trigger_price: Decimal, 
                 order_price: t.Optional[Decimal]=None):
        self.amount = amount
        self.trigger_price = trigger_price
        self.order_price = order_price
        self.side: t.Optional[OrderSide] = None # Shouldn't be set by user

    def create(self) -> StopLossOrder:
        return StopLossOrder(self.side, self.amount, 
                             self.trigger_price, self.order_price)


class MarketOrder(Order):
    def __init__(self, side: OrderSide, amount: Decimal):
        super().__init__(side, OrderType.MARKET, amount)

# Limit orders have optional TP/SL
class LimitOrder(Order):
    def __init__(self, 
                 side: OrderSide,
                 amount: Decimal,
                 order_price: Decimal,
                 take_profit_factory: t.Optional[TakeProfitFactory] = None,
                 stop_loss_factory: t.Optional[StopLossFactory] = None):
        # TODO: consider collections instead of single item
        self.take_profit_factory = take_profit_factory
        self.stop_loss_factory = stop_loss_factory
        self.take_profit: t.Optional[TakeProfitOrder] = None 
        self.stop_loss: t.Optional[StopLossOrder] = None
        super().__init__(side, OrderType.LIMIT, amount, order_price)


class MarketOrderFactory(OrderFactory):
    def __init__(self, side: OrderStatus, amount: Decimal):
        self.side = side
        self.amount = amount

    def create(self) -> MarketOrder:
        return MarketOrder(self.side, self.amount)


class LimitOrderFactory(OrderFactory):
    def __init__(self, 
                 side: OrderSide,
                 amount: Decimal, 
                 order_price: Decimal, 
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
