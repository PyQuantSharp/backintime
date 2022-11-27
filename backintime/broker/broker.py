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
    StrategyOrder,
    MarketOrder, 
    LimitOrder, 
    StopLossOrder,
    TakeProfitOrder,
    MarketOrderFactory,
    LimitOrderFactory,
    StopLossFactory,
    TakeProfitFactory
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
        return self._order.status is OrderStatus.CREATED or \
               self._order.status is OrderStatus.ACTIVATED

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
    take_profit_id: t.Optional[int] = None
    stop_loss_id: t.Optional[int] = None


class LimitOrderInfo(OrderInfo):
    def __init__(self, order_id: int, order, strategy_orders: StrategyOrders):
        self._strategy_orders = strategy_orders
        super().__init__(order_id, order)

    @property 
    def take_profit(self) -> t.Optional[StrategyOrderInfo]:
        take_profit = self._order.take_profit
        if take_profit:
            return StrategyOrderInfo(self._strategy_orders.take_profit_id,
                                     take_profit)

    @property
    def stop_loss(self) -> t.Optional[StrategyOrderInfo]:
        stop_loss = self._order.stop_loss
        if stop_loss:
            return StrategyOrderInfo(self._strategy_orders.stop_loss_id,
                                     stop_loss)


class AbstractBroker(ABC):
    @abstractmethod
    def get_balance(self) -> BalanceInfo:
        pass
    
    @abstractmethod
    def get_fiat_balance(self) -> float:
        pass
    
    @abstractmethod
    def get_crypto_balance(self) -> float:
        pass

    @abstractmethod
    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        pass

    @abstractmethod
    def submit_market_order(
                self, 
                order_factory: MarketOrderFactory) -> OrderInfo:
        pass

    @abstractmethod
    def submit_limit_order(
                self, 
                order_factory: LimitOrderFactory) -> LimitOrderInfo:
        pass

    @abstractmethod
    def submit_take_profit_order(
                self, 
                order_factory: TakeProfitFactory) -> StrategyOrderInfo:
        pass

    @abstractmethod
    def submit_stop_loss_order(
                self, 
                order_factory: StopLossFactory) -> StrategyOrderInfo:
        pass

    @abstractmethod
    def cancel_order(self, order_id: int) -> None:
        pass


class OrdersRepository:
    def __init__(self):
        self._market_orders: t.Set[int] = []    # Market/Strategy ids
        self._limit_orders: t.Set[int] = set()    # Limit/Strategy ids
        self._strategy_orders: t.Set[int] = set()   # Strategy ids
        self._orders_counter = count()
        self._orders_map: t.Dict[int, Order] = {}
        self._linked_strategy_orders: t.Dict[int, StrategyOrders] = {}

    def get_order(self, order_id: int) -> t.Optional[Order]:
        order = self._orders_map.get(order_id)

    def get_market_orders(self):
        for order_id in self._market_orders.copy():
            yield (order_id, self._orders_map[order_id])

    def get_limit_orders(self):
        for order_id in self._limit_orders.copy():
            yield (order_id, self._orders_map[order_id])

    def get_strategy_orders(self):
        for order_id in self._strategy_orders.copy():
            yield (order_id, self._orders_map[order_id])

    def get_linked_orders(self, order_id: int) -> StrategyOrders:
        return self._linked_strategy_orders[order_id]

    def add_market_order(self, order: MarketOrder) -> int:
        order_id = next(self._orders_counter)
        self._market_orders.append(order_id)
        self._orders_map[order_id] = order
        return order_id 

    def add_limit_order(self, order: LimitOrder) -> int:
        order_id = next(self._orders_counter)
        self._limit_orders.add(order_id)
        self._orders_map[order_id] = order
        # Create shared obj for linked TP/SL orders 
        strategy_orders = StrategyOrders()
        self._linked_strategy_orders[order_id] = strategy_orders 
        return order_id

    def add_take_profit_order(self, order: TakeProfitOrder) -> int:
        return self._add_strategy_order(order)

    def add_stop_loss_order(self, order: StopLossOrder) -> int:
        return self._add_strategy_order(order)

    def add_linked_take_profit_order(self, 
                                     order: TakeProfitOrder, 
                                     limit_order_id: int) -> int:
        order_id = self._add_strategy_order(order)
        limit_order = self._orders_map[limit_order_id]
        limit_order.take_profit = order
        # NOTE: StrategyOrders is shared with LimitOrderInfo 
        linked = self._linked_strategy_orders[limit_order_id]
        linked.take_profit_id = order_id
        return order_id

    def add_linked_stop_loss_order(self, 
                                   order: StopLossOrder, 
                                   limit_order_id: int) -> int:
        order_id = self._add_strategy_order(order)
        limit_order = self._orders_map[limit_order_id]
        limit_order.stop_loss = order
        # NOTE: StrategyOrders is shared with LimitOrderInfo
        linked = self._linked_strategy_orders[limit_order_id]
        linked.stop_loss_id = order_id
        return order_id

    def add_order_to_market_orders(self, order_id: int) -> None:
        self._market_orders.add(order_id)

    def add_order_to_limit_orders(self, order_id: int) -> None:
        self._limit_orders.add(order_id)

    def remove_market_orders(self) -> None:
        self._market_orders = []

    def remove_market_order(self, order_id: int) -> None:
        self._market_orders.remove(order_id)

    def remove_limit_order(self, order_id: int) -> None:
        self._limit_orders.remove(order_id)

    def remove_take_profit_order(self, order_id: int) -> None:
        self.remove_strategy_order(order_id)

    def remove_stop_loss_order(self, order_id: int) -> None:
        self.remove_strategy_order(order_id)

    def remove_strategy_order(self, order_id: int) -> None:
        if order_id in self._limit_orders:
            self._limit_orders.remove(order_id)
        if order_id in self._market_orders:
            self._market_orders.remove(order_id)
        if order_id in self._strategy_orders:
            self._strategy_orders.remove(order_id)

    def _add_strategy_order(self, order: StrategyOrder) -> int:
        order_id = next(self._orders_counter)
        self._limit_orders.add(order_id)
        self._strategy_orders.add(order_id)
        self._orders_map[order_id] = order
        return order_id


class OrderNotFound(Exception):
    def __init__(self, order_id: int):
        super().__init__(f"Order with `order_id`={order_id} was not found")


class Broker(AbstractBroker):
    def get_balance(self) -> BalanceInfo:
        pass

    def get_fiat_balance(self) -> float:
        pass
    
    def get_crypto_balance(self) -> float:
        pass

    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        pass

    def submit_market_order(
                self, 
                order_factory: MarketOrderFactory) -> OrderInfo:
        pass

    def submit_limit_order(
                self, 
                order_factory: LimitOrderFactory) -> LimitOrderInfo:
        pass

    def submit_take_profit_order(
                self, 
                order_factory: TakeProfitFactory) -> StrategyOrderInfo:
        pass

    def submit_stop_loss_order(
                self, 
                order_factory: StopLossFactory) -> StrategyOrderInfo:
        pass

    def cancel_order(self, order_id: int) -> None:
        pass
