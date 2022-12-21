"""Base validation for orders. Only check that prices and amounts > 0."""
from .base import InvalidOrderData
from .orders import (
    MarketOrder, 
    LimitOrder, 
    TakeProfitOrder, 
    StopLossOrder, 
    TakeProfitFactory, 
    StopLossFactory
)


def validate_market_order(order: MarketOrder) -> None:
    if order.amount <= 0:
        raise InvalidOrderData("[MarketOrder]: `amount` must be > 0")


def validate_take_profit_factory(factory: TakeProfitFactory) -> None:
    message = ''
    if factory.amount <= 0:
        message += "`amount` must be > 0. "
    if factory.trigger_price <= 0:
        message += "`trigger_price` must be > 0. "
    if factory.order_price and factory.order_price <= 0:
        message += "`order_price` must be > 0. "
    if message:
        raise InvalidOrderData(f"[TakeProfitOrder]: {message}")


def validate_stop_loss_factory(factory: StopLossFactory) -> None:
    message = ''
    if factory.amount <= 0:
        message += "`amount` must be > 0. "
    if factory.trigger_price <= 0:
        message += "`trigger_price` must be > 0. "
    if factory.order_price and factory.order_price <= 0:
        message += "`order_price` must be > 0. "
    if message:
        raise InvalidOrderData(f"[StopLossOrder]: {message}")


def validate_limit_order(order: LimitOrder) -> None:
    message = ''
    if order.amount <= 0:
        message += "`amount` must be > 0. "
    if order.order_price <= 0:
        message += "`order_price` must be > 0. "
    if order.take_profit_factory:
        try:
            validate_take_profit_factory(order.take_profit_factory)
        except InvalidOrderData as e:
            message += str(e)
    if order.stop_loss_factory:
        try:
            validate_stop_loss_factory(order.stop_loss_factory)
        except InvalidOrderData as e:
            message += str(e)
    if message:
        raise InvalidOrderData(f"[LimitOrder]: {message}")


def validate_take_profit(order: TakeProfitOrder) -> None:
    message = ''
    if order.amount <= 0:
        message += "`amount` must be > 0. "
    if order.trigger_price <= 0:
        message += "`trigger_price` must be > 0. "
    if order.order_price and order.order_price <= 0:
        message += "`order_price` must be > 0. "
    if message:
        raise InvalidOrderData(f"[TakeProfitOrder]: {message}")


def validate_stop_loss(order: StopLossOrder) -> None:
    message = ''
    if order.amount <= 0:
        message += "`amount` must be > 0. "
    if order.trigger_price <= 0:
        message += "`trigger_price` must be > 0. "
    if order.order_price and order.order_price <= 0:
        message += "`order_price` must be > 0. "
    if message:
        raise InvalidOrderData(f"[StopLossOrder]: {message}")

