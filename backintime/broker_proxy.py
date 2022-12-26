import typing as t
from decimal import Decimal
from .broker.base import (
    Trade, 
    OrderInfo, 
    LimitOrderInfo, 
    StrategyOrderInfo,
    AbstractBroker,
    AbstractBalance
)
from .broker.orders import (
    OrderSide,
    OrderFactory,
    MarketOrderFactory,
    LimitOrderFactory,
    TakeProfitFactory,
    StopLossFactory
)


class BrokerProxy(AbstractBroker):
    def __init__(self, broker: AbstractBroker):
        self._broker = broker

    @property
    def balance(self) -> AbstractBalance:
        """Get balance info."""
        return self._broker.balance

    @property
    def max_fiat_for_maker(self) -> Decimal:
        """Get max available fiat for a 'maker' order."""
        return self._broker.max_fiat_for_maker

    @property
    def max_fiat_for_taker(self) -> Decimal:
        """Get max available fiat for a 'taker' order."""
        return self._broker.max_fiat_for_taker

    def iter_orders(self) -> t.Iterator[OrderInfo]:
        """Get orders iterator."""
        return self._broker.iter_orders()

    def iter_trades(self) -> t.Iterator[Trade]:
        """Get trades iterator."""
        return self._broker.iter_trades()

    def get_orders(self) -> t.Sequence[OrderInfo]:
        """Get sequence of orders."""
        return self._broker.get_orders()

    def get_trades(self) -> t.Sequence[Trade]:
        """Get sequence of trades."""
        return self._broker.get_trades()

    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        """Submit order for execution."""
        return self._broker.submit_order(order_factory)

    def submit_market_order(
                self, 
                order_factory: MarketOrderFactory) -> OrderInfo:
        """Submit market order."""
        return self._broker.submit_market_order(order_factory)

    def submit_limit_order(
                self, 
                order_factory: LimitOrderFactory) -> LimitOrderInfo:
        """Submit limit order."""
        return self._broker.submit_limit_order(order_factory)

    def submit_take_profit_order(
                self, 
                order_side: OrderSide,
                order_factory: TakeProfitFactory) -> StrategyOrderInfo:
        """Submit Take Profit order."""
        return self._broker.submit_take_profit_order(order_side, order_factory)

    def submit_stop_loss_order(
                self, 
                order_side: OrderSide,
                order_factory: StopLossFactory) -> StrategyOrderInfo:
        """Submit Stop Loss order."""
        return self._broker.submit_stop_loss_order(order_side, order_factory)

    def cancel_order(self, order_id: int) -> None:
        """Cancel order by id."""
        return self._broker.cancel_order(order_id)
