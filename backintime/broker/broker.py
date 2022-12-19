import typing as t
from datetime import datetime
from itertools import count
from decimal import Decimal    # https://docs.python.org/3/library/decimal.html
from .balance import Balance, BalanceInfo
from .fees import FeesEstimator
from .repo import OrdersRepository
from .base import (
    Trade,
    OrderInfo,
    LimitOrderInfo,
    StrategyOrders,
    StrategyOrderInfo,
    validate_market_order,
    validate_limit_order,
    validate_take_profit_factory,
    validate_stop_loss_factory,
    BrokerException,
    OrderSubmissionError,
    OrderCancellationError,
    AbstractBroker
)
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


_match_predicates = (
    lambda price, candle: price == candle.open,
    lambda price, candle: price >= candle.low and price <= candle.high,
    lambda price, candle: price == candle.close
)


class OrderNotFound(OrderCancellationError):
    def __init__(self, order_id: int):
        message = f"Order with order_id={order_id} was not found"
        super().__init__(message)


class Broker(AbstractBroker):
    """
    Broker provides orders management in a simulated
    market environment. The broker executes/activates orders
    whose conditions fits the market every time the `update`
    method is called.

    Order Execution Policy:

    - Market orders: 
        All market orders will be executed when 
        the `update` method is called. 
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
        are applied to order's `trigger_price`. 
        When a TP/SL order is triggered, it will be treated
        as a market or limit order, depending on whether 
        `order_price` is set for the order. 
    """
    def __init__(self, start_money: Decimal, fees: FeesEstimator):
        assert start_money > 0, "Start money must be greater than zero"
        self._fees = fees
        self._balance = Balance(fiat_balance=start_money)
        self._balance_info = BalanceInfo(self._balance)
        self._orders = OrdersRepository()
        # Shared positions for TP/SL orders
        self._shared_buy_position = Decimal(0)
        self._shared_sell_position = Decimal(0)
        # Summarised TP/SL orders positions
        self._aggregated_buy_position = Decimal(0)
        self._aggregated_sell_position = Decimal(0)
        # Let's just make it as a simple list as for now
        self._trades_counter = count()
        self._trades: t.List[Trade] = []
        # Close time of the current candle
        self._current_time: t.Optional[datetime] = None

    def iter_orders(self) -> t.Iterator[OrderInfo]:
        """Get orders iterator."""
        for order_id, order in self._orders:
            yield OrderInfo(order_id, order) 

    def get_orders(self) -> t.List[OrderInfo]:
        """Get orders list."""
        return list(self.iter_orders)

    def iter_trades(self) -> t.Iterator[Trade]:
        """Get trades iterator."""
        return iter(self._trades)

    def get_trades(self) -> t.List[Trade]:
        """Get trades list."""
        return list(self._trades)

    def _add_trade(self, order_id: int, order: Order) -> None:
        """Add new trade."""
        # TODO: consider concrete trades with OrderInfo subclasses
        trade_id = next(self._trades_counter)
        order_info = OrderInfo(order_id, order)
        balance = self._balance.fiat_balance
        self._trades.append(Trade(trade_id, order_info, balance))

    @property
    def balance(self) -> BalanceInfo:
        """Get balance info."""
        return self._balance_info

    def get_max_fiat_for_taker(self) -> Decimal:
        """Get max available fiat for a 'taker' order."""
        available_fiat = self._balance.available_fiat_balance
        return available_fiat / (1 + self._fees.taker_fee)

    def get_max_fiat_for_maker(self) -> Decimal:
        """Get max available fiat for a 'maker' order"""
        available_fiat = self._balance.available_fiat_balance
        return available_fiat / (1 + self._fees.maker_fee)

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
        order = order_factory.create(self._current_time)
        validate_market_order(order)
        self._hold_funds(order)
        order_id = self._orders.add_market_order(order)
        return OrderInfo(order_id, order)

    def submit_limit_order(
                self, 
                order_factory: LimitOrderFactory) -> LimitOrderInfo:
        """Submit limit order."""
        order = order_factory.create(self._current_time)
        validate_limit_order(order)
        self._hold_funds(order)
        order_id = self._orders.add_limit_order(order)
        strategy_orders = self._orders.get_linked_orders(order_id)
        return LimitOrderInfo(order_id, order, strategy_orders)

    def submit_take_profit_order(
                self, 
                order_side: OrderSide,
                order_factory: TakeProfitFactory) -> StrategyOrderInfo:
        """Submit Take Profit order."""
        order = order_factory.create(self._current_time)
        validate_take_profit_factory(order_factory)
        order.side = order_side
        self._hold_position(order)
        order_id = self._orders.add_take_profit_order(order)
        return StrategyOrderInfo(order_id, order)

    def submit_stop_loss_order(
                self, 
                order_side: OrderSide,
                order_factory: StopLossFactory) -> StrategyOrderInfo:
        """Submit Stop Loss order."""
        order = order_factory.create(self._current_time)
        validate_stop_loss_factory(order_factory)
        order.side = order_side
        self._hold_position(order)
        order_id = self._orders.add_stop_loss_order(order)
        return StrategyOrderInfo(order_id, order)

    def _submit_linked_take_profit(self, 
                                   take_profit_factory: TakeProfitFactory,
                                   limit_order_id: int) -> None:
        """Submit new linked TP from limit order."""
        order = take_profit_factory.create(self._current_time)
        self._hold_position(order)
        self._orders.add_linked_take_profit_order(order, limit_order_id)

    def _submit_linked_stop_loss(self, 
                                 stop_loss_factory: StopLossFactory, 
                                 limit_order_id: int) -> None:
        """Submit new linked SL from limit order."""
        order = stop_loss_factory.create(self._current_time)
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
            total_price = self._get_total_price(order)
            self._balance.hold_fiat(total_price)
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
            total_price = self._get_total_price(order)
            if total_price <= self._balance.available_fiat_balance:
                # If total amount fits, hold funds and 
                # make it shared for other TP/SL
                self._balance.hold_fiat(total_price)
                self._shared_buy_position += total_price
            else:
                # Acquire only insufficient
                hold_amount = total_price - self._shared_buy_position
                self._balance.hold_fiat(hold_amount)
            self._aggregated_buy_position += total_price

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
            total_price = self._get_total_price(order)
            self._balance.release_fiat(total_price)
        elif order.side is OrderSide.SELL:
            self._balance.release_crypto(order.amount)

    def _release_position(self, order: StrategyOrder) -> None:
        if order.side is OrderSide.BUY:
            # Decrease value in aggregated position for BUY
            total_price = self._get_total_price(order)
            self._aggregated_buy_position -= total_price 
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

    def _get_total_price(self, order: Order) -> Decimal:
        """
        Estimate total amount of funds required to execute the order
        including execution fee. For BUY orders only.
        """
        if order.order_price:   # Limit
            price, _ = self._get_maker_price(order)
            return price
        else:                   # Market 
            price, _ = self._get_taker_price(order)
            return price

    def _get_maker_price(self, order) -> t.Tuple[Decimal, Decimal]:
        """
        Estimate total amount of funds required to execute the order
        including maker fee. Return amount and calculated fee.
        For BUY orders only.
        """
        price = self._fees.estimate_maker_price(order.amount)
        fee = price - order.amount
        return price, fee

    def _get_taker_price(self, order) -> t.Tuple[Decimal, Decimal]:
        """
        Estimate total amount of funds required to execute the order
        including taker fee. Return amount and calculated fee.
        For BUY orders only.
        """
        price = self._fees.estimate_taker_price(order.amount)
        fee = price - order.amount
        return price, fee

    def _get_maker_gain(self, order) -> t.Tuple[Decimal, Decimal]:
        """
        Estimate gain minus maker fee. Return gain and calculated fee.
        For SELL orders only.
        """
        total_amount = order.amount * order.order_price
        gain = self._fees.estimate_maker_gain(total_amount)
        fee = total_amount - gain
        return gain, fee

    def _get_taker_gain(self, 
                        order, 
                        market_price: Decimal) -> t.Tuple[Decimal, Decimal]:
        """
        Estimate gain minus taker fee. Return gain and calculated fee. 
        For SELL orders only.
        """
        total_amount = order.amount * market_price
        gain = self._fees.estimate_taker_gain(total_amount)
        fee = total_amount - gain
        return gain, fee

    def _cancel_strategy_orders(self) -> None:
        """
        Cancel all strategy orders. 
        Must be invoked on position modification.
        """
        for order_id, order in self._orders.get_strategy_orders():
            self._release_position(order)
            self._orders.remove_strategy_order(order_id)
            order.status = OrderStatus.SYS_CANCELLED

    def update(self, candle) -> None:
        """Review whether orders can be executed."""
        self._current_time = candle.close_time
        # Execute all market orders
        self._execute_market_orders(candle.open)
        # Review orders with limited price 
        for match_predicate in _match_predicates:
            for order_id, order in self._orders.get_limit_orders():
                # Review strategy orders
                if isinstance(order, StrategyOrder):
                    if order.status is OrderStatus.CREATED:
                        if match_predicate(order.trigger_price, candle):
                            self._activate_strategy_order(order_id, order)
                    elif order.status is OrderStatus.ACTIVATED:
                        if match_predicate(order.order_price, candle):
                            self._execute_strategy_limit_order(order_id, order)
                # Review limit orders
                elif isinstance(order, LimitOrder):
                    if match_predicate(order.order_price, candle):
                        self._execute_limit_order(order_id, order)

    def _execute_market_orders(self, market_price: Decimal) -> None:
        for order_id, order in self._orders.get_market_orders():
            if isinstance(order, MarketOrder):
                self._execute_market_order(order_id, order, market_price)
            elif isinstance(order, StrategyOrder):
                self._execute_strategy_market_order(order_id, order, market_price)
        self._orders.remove_market_orders()

    def _execute_market_order(self, 
                              order_id: int,
                              order: MarketOrder,
                              market_price: Decimal) -> None:
        if order.side is OrderSide.BUY:
            price, fee = self._get_taker_price(order)
            order.trading_fee = fee
            self._balance.withdraw_fiat(price)
            self._balance.deposit_crypto(order.amount / market_price)

        elif order.side is OrderSide.SELL:
            gain, fee = self._get_taker_gain(order, market_price)
            order.trading_fee = fee
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(gain)

        order.status = OrderStatus.EXECUTED
        order.fill_price = market_price
        order.date_updated = self._current_time
        self._add_trade(order_id, order)
        # Cancel all TP/SL orders since position was modified
        self._cancel_strategy_orders()

    def _execute_limit_order(self, 
                             order_id: int, 
                             order: LimitOrder) -> None:
        if order.side is OrderSide.BUY:
            price, fee = self._get_maker_price(order)
            order.trading_fee = fee
            self._balance.withdraw_fiat(price)
            self._balance.deposit_crypto(order.amount / order.order_price)

        elif order.side is OrderSide.SELL:
            gain, fee = self._get_maker_gain(order)
            order.trading_fee = fee
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(gain)

        order.status = OrderStatus.EXECUTED
        order.fill_price = order.order_price
        order.date_updated = self._current_time
        self._orders.remove_limit_order(order_id)
        self._add_trade(order_id, order)
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
        order.date_activated = self._current_time
        order.date_updated = self._current_time

    def _execute_strategy_market_order(self, 
                                       order_id: int, 
                                       order: StrategyOrder, 
                                       market_price: Decimal) -> None:
        if order.side is OrderSide.BUY:
            price, fee = self._get_taker_price(order)
            order.trading_fee = fee
            self._balance.withdraw_fiat(price)
            self._balance.deposit_crypto(order.amount / market_price)
            self._aggregated_buy_position -= price

        elif order.side is OrderSide.SELL:
            gain, fee = self._get_taker_gain(order, market_price)
            order.trading_fee = fee
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(gain)
            self._aggregated_sell_position -= order.amount 

        order.status = OrderStatus.EXECUTED
        order.fill_price = market_price
        order.date_updated = self._current_time
        self._orders.remove_strategy_order(order_id)
        self._add_trade(order_id, order)
        # Cancel all other TP/SL orders since position was modified
        self._cancel_strategy_orders()

    def _execute_strategy_limit_order(self, 
                                      order_id: int, 
                                      order: StrategyOrder) -> None:
        if order.side is OrderSide.BUY:
            price, fee = self._get_maker_price(order)
            order.trading_fee = fee
            self._balance.withdraw_fiat(price)
            self._balance.deposit_crypto(order.amount / order.order_price)
            self._aggregated_buy_position -= price

        elif order.side is OrderSide.SELL:
            gain, fee = self._get_maker_gain(order)
            order.trading_fee = fee
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(gain)
            self._aggregated_sell_position -= order.amount 

        order.status = OrderStatus.EXECUTED
        order.fill_price = order.order_price
        order.date_updated = self._current_time
        self._orders.remove_strategy_order(order_id)
        self._add_trade(order_id, order)
        # Cancel all other TP/SL orders since position was modified
        self._cancel_strategy_orders()
