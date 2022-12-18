import typing as t
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod
from decimal import Decimal    # https://docs.python.org/3/library/decimal.html
from .orders import (
    OrderSide,
    Order, 
    OrderType,
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


class BrokerException(Exception):
    """Base class for all broker-related exceptions."""
    pass


class OrderSubmissionError(BrokerException):
    """Generic exception for order submission error."""
    pass


class InvalidOrderData(OrderSubmissionError):
    """Order submission failed because order data is invalid."""
    pass


class InsufficientFunds(OrderSubmissionError):
    """Order submission failed due to insufficient funds."""
    pass


class OrderCancellationError(BrokerException):
    """Generic exception for order cancellation error."""
    pass


# Implementation for orders & trades
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
    def order_type(self) -> OrderType:
        return self._order.order_type

    @property
    def order_side(self) -> OrderSide:
        return self._order.side

    @property 
    def amount(self) -> Decimal:
        return self._order.amount

    @property
    def date_created(self) -> datetime:
        return self._order.date_created

    @property 
    def order_price(self) -> t.Optional[Decimal]:
        return self._order.order_price

    @property 
    def status(self) -> OrderStatus:
        return self._order.status

    @property
    def date_updated(self) -> datetime:
        return self._order.date_updated

    @property
    def fill_price(self) -> t.Optional[Decimal]:
        return self._order.fill_price

    @property
    def trading_fee(self) -> t.Optional[Decimal]:
        return self._order.trading_fee

    @property 
    def is_unfulfilled(self) -> bool:
        return not self._order.fill_price

    @property 
    def is_canceled(self) -> bool:
        return self._order.status is OrderStatus.CANCELLED or \
                self._order.status is OrderStatus.SYS_CANCELLED

    @property 
    def is_executed(self) -> bool:
        return self._order.status is OrderStatus.EXECUTED


class StrategyOrderInfo(OrderInfo):
    @property
    def trigger_price(self) -> Decimal:
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


class Trade:
    def __init__(self, 
                 trade_id: int, 
                 order_info: OrderInfo, 
                 result_balance: Decimal):
        self._trade_id = trade_id
        self._order_info = order_info
        self._result_balance = result_balance

    @property
    def trade_id(self) -> int:
        return self._trade_id

    @property
    def order(self) -> OrderInfo:
        # Info about the order
        return self._order_info
    
    @property
    def result_balance(self) -> Decimal:
        # fiat balance at the moment of order execution
        return self._result_balance


class AbstractBalance:
    @property
    @abstractmethod
    def available_fiat_balance(self) -> Decimal:
        """Get fiat available for trading."""
        pass

    @property
    @abstractmethod
    def available_crypto_balance(self) -> Decimal:
        """Get crypto available for trading."""
        pass

    @property
    @abstractmethod
    def fiat_balance(self) -> Decimal:
        """Get fiat balance."""
        pass

    @property
    @abstractmethod
    def crypto_balance(self) -> Decimal:
        """Get crypto balance."""
        pass


class AbstractBroker(ABC):
    """
    Broker provides orders management in a simulated
    market environment.
    """
    @abstractmethod
    def get_balance(self) -> AbstractBalance:
        """Get balance info."""
        pass

    @abstractmethod
    def get_max_fiat_for_taker(self) -> Decimal:
        """Get max available fiat for a 'taker' order."""
        pass

    @abstractmethod
    def get_max_fiat_for_maker(self) -> Decimal:
        """Get max available fiat for a 'maker' order."""
        pass

    @abstractmethod
    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        """Submit order for execution."""
        pass

    @abstractmethod
    def submit_market_order(
                self, 
                order_factory: MarketOrderFactory) -> OrderInfo:
        """Submit market order."""
        pass

    @abstractmethod
    def submit_limit_order(
                self, 
                order_factory: LimitOrderFactory) -> LimitOrderInfo:
        """Submit limit order."""
        pass

    @abstractmethod
    def submit_take_profit_order(
                self, 
                order_factory: TakeProfitFactory) -> StrategyOrderInfo:
        """Submit Take Profit order."""
        pass

    @abstractmethod
    def submit_stop_loss_order(
                self, 
                order_factory: StopLossFactory) -> StrategyOrderInfo:
        """Submit Stop Loss order."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: int) -> None:
        """Cancel order by id."""
        pass
    
    @abstractmethod
    def iter_orders(self) -> t.Iterator[OrderInfo]:
        """Get orders iterator."""
        pass

    @abstractmethod
    def iter_trades(self) -> t.Iterator[Trade]:
        """Get trades iterator."""
        pass

    @abstractmethod
    def get_orders(self) -> t.Sequence[OrderInfo]:
        """Get orders sequence."""
        pass

    @abstractmethod
    def get_trades(self) -> t.Sequence[Trade]:
        """Get trades sequence."""
        pass
