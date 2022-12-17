import typing as t
from .broker.broker import (
    AbstractBroker, 
    Broker, 
    BalanceInfo, 
    Trade,
    OrderInfo, 
    LimitOrderInfo, 
    StrategyOrderInfo
)
from .broker.orders import (
    OrderFactory,
    MarketOrderFactory,
    LimitOrderFactory,
    TakeProfitFactory,
    StopLossFactory
)


class BrokerProxy(AbstractBroker):
    def __init__(self, broker: Broker):
        self._broker = broker

    def get_balance(self) -> BalanceInfo:
        """Get balance info."""
        return self._broker.get_balance()

    def iter_trades(self) -> t.Iterator[Trade]:
        return self._broker.iter_trades()

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
                order_factory: TakeProfitFactory) -> StrategyOrderInfo:
        """Submit Take Profit order."""
        return self._broker.submit_take_profit_order(order_factory)

    def submit_stop_loss_order(
                self, 
                order_factory: StopLossFactory) -> StrategyOrderInfo:
        """Submit Stop Loss order."""
        return self._broker.submit_stop_loss_order(order_factory)

    def cancel_order(self, order_id: int) -> None:
        """Cancel order by id."""
        return self._broker.cancel_order(order_id)
