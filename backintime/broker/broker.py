import typing as t
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
        """Get fiat available for trading."""
        return self._data.available_fiat_balance

    @property
    def available_crypto_balance(self) -> float:
        """Get crypto available for trading."""
        return self._data.available_crypto_balance

    @property
    def fiat_balance(self) -> float:
        """Get fiat balance."""
        return self._data.fiat_balance

    @property
    def crypto_balance(self) -> float:
        """Get crypto balance."""
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
        return self._order.status is OrderStatus.CANCELLED

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
        """Get balance info."""
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


class OrderSubmissionError(Exception): pass


class OrderCancellationError(Exception): pass


MatchPredicates = t.TypeVar(
                "MatchPredicates", 
                bound=t.Generator[t.Callable[[float], bool], None, None])

def _get_match_predicates(candle) -> MatchPredicates:
    yield lambda price: price == candle.OPEN
    yield lambda price: price >= candle.LOW and price <= candle.HIGH
    yield lambda price: price == candle.CLOSE


class Broker(AbstractBroker):
    """
    Broker provides orders management in a simulated
    market environment. The broker executes/activates orders
    whose conditions fits the market every time the `_update`
    method is called.

    Order Execution Policy:

    - Market orders: 
        All market orders will be executed when 
        the `_update` method is called. 
        The price of execution is the candle's OPEN price.

    - Limit orders: 
        Each of the conditions from the following list 
        will in turn be applied to the `order_price` of each order:
            1) price == candle.OPEN
            2) price >= candle.LOW and price <= candle.HIGH
            3) price == candle.CLOSE
        The order will be executed if the condition is true. 
        The price of execution is the order's `order_price`.

    - Take Profit/Stop Loss orders: 
        The activation conditions are essentially the same
        as for limit orders, but the conditions from the list 
        are applied to order's `target_price`. 
        When a TP/SL order is triggered, it will be treated
        as a market or limit order, depending on whether 
        `order_price` is set for the order. 
    """
    def __init__(self, start_money: float): 
        # TODO: fees, trades history
        self._balance = Balance(fiat_balance = start_money)
        self._balance_info = BalanceInfo(self._balance)
        self._orders = OrdersRepository()
        # Shared positions for TP/SL orders
        self._shared_buy_position = 0
        self._shared_sell_position = 0
        # Summarised TP/SL orders positions
        self._aggregated_buy_position = 0
        self._aggregated_sell_position = 0

    def get_balance(self) -> BalanceInfo:
        """Get balance info."""
        return self._balance_info

    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        """Submit order for execution."""
        if isinstance(order_factory, MarketOrderFactory):
            return self.submit_market_order(order_factory)
        elif isinstance(order_factory, LimitOrderFactory):
            return self.submit_limit_order(order_factory)
        elif isinstance(order_factory, TakeProfitFactory):
            return self.submit_take_profit_order(order_factory)
        elif isinstance(order_factory, StopLossFactory):
            return self.submit_stop_loss_order(order_factory)
        else:
            raise OrderSubmissionError(
                        f"Can't create order from {order_factory}: "
                        f"unexpected factory type.")

    def submit_market_order(
                self, 
                order_factory: MarketOrderFactory) -> OrderInfo:
        """Submit market order."""
        order = order_factory.create()
        self._hold_funds(order)
        order_id = self._orders.add_market_order(order)
        return OrderInfo(order_id, order)

    def submit_limit_order(
                self, 
                order_factory: LimitOrderFactory) -> LimitOrderInfo:
        """Submit limit order."""
        order = order_factory.create()
        self._hold_funds(order)
        order_id = self._orders.add_limit_order(order)
        strategy_orders = self._orders.get_linked_orders(order_id)
        return LimitOrderInfo(order_id, order, strategy_orders)

    def submit_take_profit_order(
                self, 
                order_factory: TakeProfitFactory) -> StrategyOrderInfo:
        """Submit Take Profit order."""
        order = order_factory.create()
        self._hold_position(order)
        order_id = self._orders.add_take_profit_order(order)
        return StrategyOrderInfo(order_id, order)

    def submit_stop_loss_order(
                self, 
                order_factory: StopLossFactory) -> StrategyOrderInfo:
        """Submit Stop Loss order."""
        order = order_factory.create()
        self._hold_position(order)
        order_id = self._orders.add_stop_loss_order(order)
        return StrategyOrderInfo(order_id, order)

    def _submit_linked_take_profit(self, 
                                   take_profit_factory: TakeProfitFactory,
                                   limit_order_id: int) -> None:
        """Submit new linked TP from limit order."""
        order = take_profit_factory.create()
        self._hold_position(order)
        self._orders.add_linked_take_profit_order(order, limit_order_id)

    def _submit_linked_stop_loss(self, 
                                 stop_loss_factory: StopLossFactory, 
                                 limit_order_id: int) -> None:
        """Submit new linked SL from limit order."""
        order = stop_loss_factory.create()
        self._hold_position(order)
        self._orders.add_linked_stop_loss_order(order, limit_order_id)

    def cancel_order(self, order_id: int) -> None:
        """Cancel order by id."""
        order = self._orders.get_order(order_id)
        if not order:
            raise OrderNotFound(order_id)

        if not order.status is OrderStatus.CREATED and \
                not order.status is OrderStatus.ACTIVATED:
            raise OrderCancellationError(
                            f"Order can't be cancelled, because "
                            f"order status is {order.status}")

        if isinstance(order, MarketOrder):
            self._release_funds(order)
            self._orders.remove_market_order(order_id)
        elif isinstance(order, LimitOrder):
            self._release_funds(order)
            self._orders.remove_limit_order(order_id)
        elif isinstance(order, TakeProfitOrder):
            self._release_position(order)
            self._orders.remove_take_profit_order(order_id)
        elif isinstance(order, StopLossOrder):
            self._release_position(order)
            self._orders.remove_stop_loss_order(order_id)
        order.status = OrderStatus.CANCELLED

    def _hold_funds(self, order: t.Union[MarketOrder, LimitOrder]) -> None:
        """
        Ensure there are enough funds available 
        and decrease available value.
        """
        if order.side == OrderSide.BUY:
            total_amount = self._get_total_amount(order)
            self._balance.hold_fiat(total_amount)
        elif order.side == OrderSide.SELL:
            self._balance.hold_crypto(order.amount)

    def _hold_position(self, order: StrategyOrder) -> None:
        """
        Ensure there are enough funds available,  
        decrease available value and make this amount shared -  
        i.e., available to other TP/SLs.
        Should new TP/SL be posted, it can then acquire funds
        from the shared position without modifying the balance.
        """
        if order.side == OrderSide.BUY:
            total_amount = self._get_total_amount(order)
            if total_amount <= self._balance.available_fiat_balance:
                # If total amount fits, hold funds and 
                # make it shared for other TP/SL
                self._balance.hold_fiat(total_amount)
                self._shared_buy_position += total_amount
            else:
                # Acquire only insufficient
                hold_amount = total_amount - self._shared_buy_position
                self._balance.hold_fiat(hold_amount)
            self._aggregated_buy_position += total_amount

        elif order.side == OrderSide.SELL:
            if order.amount <= self._balance.available_crypto_balance:
                # If total amount fits, hold funds and 
                # make it shared for other TP/SL 
                self._balance.hold_crypto(order.amount)
                self._shared_sell_position += order.amount 
            else:
                # Acquire only insufficient
                hold_amount = order.amount - self._shared_sell_position
                self._balance.hold_crypto(hold_amount)
            self._aggregated_sell_position += order.amount

    def _release_funds(self, order: t.Union[MarketOrder, LimitOrder]) -> None:
        """Increase funds available for trading."""
        if order.side is OrderSide.BUY:
            total_amount = self._get_total_amount(order)
            self._balance.release_fiat(total_amount)
        elif order.side is OrderSide.SELL:
            self._balance.release_crypto(order.amount)

    def _release_position(self, order: StrategyOrder) -> None:
        if order.side is OrderSide.BUY:
            # Decrease value in aggregated position for BUY
            total_amount = self._get_total_amount(order)
            self._aggregated_buy_position -= total_amount 
            aggregated_position = self._aggregated_buy_position
            # Decrease shared BUY position if needed
            if aggregated_position < self._shared_buy_position:
                self._shared_buy_position = aggregated_position
            # Release difference between balance and aggr. position
            fiat_balance = self._balance.fiat_balance
            fiat_available= self._balance.available_fiat_balance
            aggregated_buy = aggregated_position

            to_release = fiat_balance - aggregated_buy - fiat_available
            if to_release:
                self._balance.release_fiat(to_release)

        elif order.side is OrderSide.SELL:
            # Decrease value in aggregated postion for SELL
            self._aggregated_sell_position -= order.amount
            aggregated_position = self._aggregated_sell_position
            # Decrease shared SELL position if needed
            if aggregated_position < self._shared_sell_position:
                self._shared_sell_position = aggregated_position
            # Release difference between balance and aggr. position
            crypto_balance = self._balance.crypto_balance
            crypto_available = self._balance.available_crypto_balance
            aggregated_sell = aggregated_position

            to_release = crypto_balance - aggregated_sell - crypto_available
            if to_release:
                self._balance.release_crypto(to_release)

    def _get_total_amount(self, order: Order) -> float:
        """
        Get the total price of order (if order has price)
        or amount in the order (if order's price is market).
        """
        return order.amount * order.order_price if order.order_price \
                else order.amount

    def _cancel_strategy_orders(self) -> None:
        """
        Cancel all strategy orders. 
        Must be invoked on position modification.
        """
        for order_id, order in self._orders.get_strategy_orders():
            self._release_position(order)
            self._orders.remove_strategy_order(order_id)
            order.status = OrderStatus.CANCELLED

    def _update(self, candle) -> None:
        """Review whether orders can be executed."""
        # Execute all market orders
        self._execute_market_orders()
        # Review whether limit orders 
        for match_predicate in _get_match_predicates(candle):
            for order_id, order in self._orders.get_limit_orders():
                # Review strategy orders
                if isinstance(order, StrategyOrder):
                    if order.status is OrderStatus.CREATED:
                        if match_predicate(order.target_price):
                            self._activate_strategy_order(order_id, order)
                    elif order.status is OrderStatus.ACTIVATED:
                        if match_predicate(order.order_price):
                            self._execute_strategy_limit_order(order_id, order)
                # Review limit orders
                elif isinstance(order, LimitOrder):
                    if match_predicate(order.order_price):
                        self._execute_limit_order(order_id, order)

    def _execute_market_orders(self, market_price: float) -> None:
        for order_id, order in self._orders.get_market_orders():
            if isinstance(order, MarketOrder):
                self._execute_market_order(order, market_price)
            elif isinstance(order, StrategyOrder):
                self._execute_strategy_market_order(order_id, order, market_price)
        self._orders.remove_market_orders()

    def _execute_market_order(self, 
                              order: MarketOrder,
                              market_price: float) -> None:
        if order.side is OrderSide.BUY:
            self._balance.withdraw_fiat(order.amount) # Total amount?
            self._balance.deposit_crypto(order.amount / market_price)

        elif order.side is OrderSide.SELL:
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(order.amount * market_price)

        order.status = OrderStatus.EXECUTED
        order.fill_price = market_price
        # Cancel all TP/SL orders since position was modified
        self._cancel_strategy_orders()

    def _execute_limit_order(self, 
                             order_id: int, 
                             order: LimitOrder) -> None:
        if order.side is OrderSide.BUY:
            total_amount = self._get_total_amount(order)
            self._balance.withdraw_fiat(total_amount)
            self._balance.deposit_crypto(order.amount)

        elif order.side is OrderSide.SELL:
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(order.amount * order.order_price)

        order.status = OrderStatus.EXECUTED
        order.fill_price = order.order_price
        self._orders.remove_limit_order(order_id)
        # Cancel all TP/SL orders since position was modified
        self._cancel_strategy_orders()
        # Submit TP/SL orders, if any
        # Invert order side 
        order_side = OrderSide.BUY if order.side is OrderSide.SELL \
                        else OrderSide.SELL 
        if order.take_profit_factory:
            order.take_profit_factory.side = order_side
            self._submit_linked_take_profit(order.take_profit_factory, order_id)            
        if order.stop_loss_factory:
            order.stop_loss_factory.side = order_side 
            self._submit_linked_stop_loss(order.stop_loss_factory, order_id)

    def _activate_strategy_order(self, 
                                 order_id: int, 
                                 order: StrategyOrder) -> None:
        if order.order_price:
            self._orders.add_order_to_limit_orders(order_id)
        else:
            self._orders.add_order_to_market_orders(order_id)
        order.status = OrderStatus.ACTIVATED

    def _execute_strategy_market_order(self, 
                                       order_id: int, 
                                       order: StrategyOrder, 
                                       market_price: float) -> None:
        if order.side is OrderSide.BUY:
            self._balance.withdraw_fiat(order.amount) # Total amount?
            self._balance.deposit_crypto(order.amount / market_price)
            self._aggregated_buy_position -= total_amount

        elif order.side is OrderSide.SELL:
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(order.amount * market_price)
            self._aggregated_sell_position -= order.amount 

        order.status = OrderStatus.EXECUTED
        order.fill_price = market_price
        self._orders.remove_strategy_order(order_id)
        # Cancel all other TP/SL orders since position was modified
        self._cancel_strategy_orders()

    def _execute_strategy_limit_order(self, 
                                      order_id: int, 
                                      order: StrategyOrder) -> None:
        if order.side is OrderSide.BUY:
            total_amount = self._get_total_amount(order)
            self._balance.withdraw_fiat(total_amount)
            self._balance.deposit_crypto(order.amount)
            self._aggregated_buy_position -= total_amount

        elif order.side is OrderSide.SELL:
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(order.amount * order.order_price)
            self._aggregated_sell_position -= order.amount 

        order.status = OrderStatus.EXECUTED
        order.fill_price = order.order_price
        self._orders.remove_strategy_order(order_id)
        # Cancel all other TP/SL orders since position was modified
        self._cancel_strategy_orders()
