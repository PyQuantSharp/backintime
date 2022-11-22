import typing as t
import functools
from dataclasses import dataclass
from abc import ABC, abstractmethod
from itertools import count
from .balance import Balance
from .orders import (
    OrderSide,
    Order, 
    OrderStatus, 
    OrderFactory, 
    MarketOrder, 
    LimitOrder, 
    StopLossOrder,
    TakeProfitOrder
)


class BalanceInfo:
    """
    Wrapper around `Balance` that provides a read-only view
    into the wrapped `Balance` data.
    """
    def __init__(self, data: Balance):
        self._data = data

    @property
    def available_fiat_balance(self) -> float:
        return self._data.available_fiat_balance

    @property
    def available_crypto_balance(self) -> float:
        return self._data.available_crypto_balance
    
    @property
    def fiat_balance(self) -> float:
        return self._data.fiat_balance

    @property
    def crypto_balance(self) -> float:
        return self._data.crypto_balance


class OrderInfo:
    """
    Wrapper around `Order` that provides a read-only view
    into the wrapped `Order` data.
    """
    def __init__(self, order_id: int, order: Order):
        self._order_id = order_id
        self._order = order

    @property
    def order_id(self) -> int:
        return self._order_id

    @property 
    def amount(self) -> float:
        return self._order.amount

    @property 
    def order_price(self) -> t.Optional[float]:
        return self._order.order_price

    @property 
    def status(self) -> OrderStatus:
        return self._order.status

    @property 
    def is_unfulfilled(self) -> bool:
        return self._order.status is OrderStatus.CREATED

    @property 
    def is_canceled(self) -> bool:
        return self._order.status is OrderStatus.CANCELED

    @property 
    def is_executed(self) -> bool:
        return self._order.status is OrderStatus.EXECUTED


class StrategyOrderInfo(OrderInfo):
    @property
    def trigger_price(self) -> float:
        return self._order.trigger_price

    @property
    def is_activated(self) -> bool:
        return self._order.status is OrderStatus.ACTIVATED


@dataclass
class StrategyOrders:
    take_profit: t.Optional[StrategyOrderInfo] = None 
    stop_loss: t.Optional[StrategyOrderInfo] = None 


class LimitOrderInfo(OrderInfo):
    def __init__(self, order_id: int, order, strategy_orders: StrategyOrders):
        self._strategy_orders = strategy_orders
        super().__init__(order_id, order)

    @property 
    def take_profit(self) -> t.Optional[StrategyOrderInfo]:
        return self._strategy_orders.take_profit

    @property
    def stop_loss(self) -> t.Optional[StrategyOrderInfo]:
        return self._strategy_orders.stop_loss


class AbstractBroker(ABC):
    @abstractmethod
    def get_balance(self) -> Balance:
        pass
    
    @abstractmethod
    def get_fiat_balance(self) -> float:
        pass
    
    @abstractmethod
    def get_crypto_balance(self) -> float:
        pass

    @abstractmethod
    def submit_order(self, order_factory: OrderFactory) -> Order:
        pass

    @abstractmethod
    def cancel_order(self, order_id: int) -> None:
        pass


class Broker(AbstractBroker):
    def get_balance(self) -> Balance:
        pass
    
    def get_fiat_balance(self) -> float:
        pass
    
    def get_crypto_balance(self) -> float:
        pass
    
    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        pass

    def cancel_order(self, order_id: int) -> None:
        pass
