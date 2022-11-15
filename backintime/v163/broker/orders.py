import typing as t
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime


class OrderStatus(Enum):
    CREATED = "CREATED"
    CANCELED = "CANCELED"
    EXECUTED = "EXECUTED"
    # Only for stop loss orders
    ACTIVATED = "ACTIVATED"


class Order:
    """ Base class for all orders """
    def __init__(self, amount: float, price: t.Optional[float]=None):
        self.amount = amount
        self.price = price
        self.status = OrderStatus.CREATED
        self.created_date = datetime.utcnow()   # TZ?
        self.canceled_date: t.Optional[datetime] = None
        self.executed_date: t.Optional[datetime] = None


class SellOrder(Order):
    # TODO: define position type
    def __init__(self, 
                 position: t.Any, 
                 amount: float, 
                 price: t.Optional[float]=None):
        self.position=position
        super().__init__(amount, price)


class MarketSellOrder(SellOrder):
    def __init__(self, position: t.Any, amount: float):
        super().__init__(position, amount)


class LimitSellOrder(SellOrder):
    def __init__(self, position: t.Any, amount: float, price: float):
        super().__init__(position, amount, price)

# TP/SL have additional functionality
#   it can be implemented as unbound function and
#   saved in hooks.
class TakeProfitOrder(SellOrder):
    # TODO: define position type
    def __init__(self, 
                 amount: float,
                 price: float,
                 position: t.Any, 
                 hooks: t.Any):
        self.hooks: t.Any = hooks
        super().__init__(position, amount, price)


class StopLossOrder(SellOrder):
    # TODO: define position type
    def __init__(self, 
                 amount: float,
                 price: float,
                 position: t.Any, 
                 hooks: t.Any):
        self.hooks: t.Any = hooks
        super().__init__(position, amount, price)

# Factories
# TODO: implement factories for all orders
class OrderFactory(ABC):
    @abstractmethod
    def create(self) -> Order:
        pass


class TakeProfitFactory(OrderFactory):
    def __init__(self):
        # TODO: define ctor params
        pass

    def create(self) -> TakeProfitOrder:
        pass


class StopLossFactory(OrderFactory):
    def __init__(self):
        # TODO: define ctor params
        pass

    def create(self) -> StopLossOrder:
        pass
# End Factories

class BuyOrder(Order):
    def __init__(self,
                 amount: float,
                 price: float = None,
                 take_profit_factory: t.Optional[TakeProfitFactory] = None,
                 stop_loss_factory: t.Optional[StopLossFactory] = None):
        self.take_profit_factory = take_profit_factory
        self.stop_loss_factory = stop_loss_factory
        self.take_profit: t.Optional[TakeProfitOrder] = None
        self.stop_loss: t.Optional[StopLossOrder] = None
        super().__init__(amount, price)


class MarketBuyOrder(BuyOrder):
    def __init__(self,
                 amount: float,
                 take_profit_factory: t.Optional[TakeProfitFactory] = None,
                 stop_loss_factory: t.Optional[StopLossFactory] = None):
        super().__init__(amount, take_profit_factory, stop_loss_factory)


class LimitBuyOrder(BuyOrder):
    def __init__(self,
                 amount: float,
                 price: float,
                 take_profit_factory: t.Optional[TakeProfitFactory] = None,
                 stop_loss_factory: t.Optional[StopLossFactory] = None):
        super().__init__(amount, price, 
                         take_profit_factory, stop_loss_factory)

# Wrappers for public usage - only getters
class OrderInfo:
    def __init__(self, order: Order):
        self._order = order

    @property 
    def amount(self) -> float:
        return self._order.amount

    @property 
    def price(self) -> t.Optional[float]:
        return self._order.price

    @property 
    def status(self) -> OrderStatus:
        return self._order.status

    @property 
    def created_date(self) -> datetime:
        return self._order.created_date

    @property 
    def canceled_date(self) -> t.Optional[datetime]:
        return self._order.canceled_date

    @property 
    def executed_date(self) -> t.Optional[datetime]:
        return self._order.executed_date

    @property 
    def is_unfulfilled(self) -> bool:
        return self._order.status is OrderStatus.CREATED

    @property 
    def is_canceled(self) -> bool:
        return self._order.status is OrderStatus.CANCELED

    @property 
    def is_executed(self) -> bool:
        return self._order.status is OrderStatus.EXECUTED


class StopLossOrderInfo(OrderInfo):
    @property
    def is_activated(self) -> bool:
        return self._order.status is OrderStatus.ACTIVATED
# End wrappers