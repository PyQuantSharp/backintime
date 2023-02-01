import typing as t
from datetime import datetime
from itertools import count
from decimal import Decimal, ROUND_FLOOR    # https://docs.python.org/3/library/decimal.html
from .balance import Balance, BalanceInfo
from .fees import FeesEstimator
from .repo import OrdersRepository
from backintime.broker.base import (
    OrderSide,
    OrderType,
    OrderStatus,
    MarketOrderOptions,
    LimitOrderOptions,
    TakeProfitOptions,
    StopLossOptions,
    BrokerException,
    OrderSubmissionError,
    OrderCancellationError,
    AbstractBroker
)
from .validators import (
    validate_market_order_options,
    validate_limit_order_options,
    validate_take_profit_options,
    validate_stop_loss_options
)
from .orders import (
    TradeInfo,
    Order,
    OrderInfo,
    MarketOrder,
    MarketOrderInfo,
    LimitOrder,
    LimitOrderInfo,
    StrategyOrder,
    StrategyOrders,
    TakeProfitOrder,
    TakeProfitInfo,
    StopLossOrder,
    StopLossInfo
)

# options --> validation --> acquire --> create --> store
# submission: create & store & return info
# create: validate & hold funds & return

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
        Limit order will be executed at the limit price or better:
        lower or equal price for BUY orders and higher or equal price 
        for SELL orders.
        First, the `order_price` of each order will be compared to
        the OPEN price of a new candle: 
            BUY orders will be executed if `order_price` >= OPEN. 
            SELL orders will be executed if `order_price` <= OPEN.

        Then, remaining BUYs will be compared to LOW,
        and remaining SELLs - to HIGH.
        Fill price is the first price that matched limit price.

    - Take Profit/Stop Loss orders: 
        TP/SL orders will be activated if the `trigger_price` is
        within the price bounds of a candle.

        This check is performed in two steps:
            1) For each order: activate if trigger_price == OPEN
            2) For each order: activate if LOW <= trigger_price <= HIGH 

        When a TP/SL order is triggered, it will be treated
        as a market or limit order, depending on whether 
        `order_price` is set for the order.

    Limit, Take Profit and Stop Loss orders are reviewed 
    in the order of their submission (oldest first).
    """
    def __init__(self, 
                 start_money: Decimal, 
                 fees: FeesEstimator,
                 min_fiat: Decimal = Decimal('0.01'),
                 min_crypto: Decimal = Decimal('0.00000001')):
        assert start_money > 0, "Start money must be greater than zero"
        self._fees = fees
        self._balance = Balance(fiat_balance=start_money,
                                min_fiat=min_fiat,
                                min_crypto=min_crypto)
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
        self._trades: t.List[TradeInfo] = []
        # Close time of the current candle
        self._current_time: t.Optional[datetime] = None
        # Close price of the current (last) candle
        self._current_price: t.Optional[Decimal] = None
        # Used for rounding
        self._min_fiat = min_fiat
        self._min_crypto = min_crypto

    @property
    def balance(self) -> BalanceInfo:
        """Get balance info."""
        return self._balance_info

    @property
    def max_fiat_for_taker(self) -> Decimal:
        """Get max available fiat for a 'taker' order."""
        available_fiat = self._balance.available_fiat_balance
        available_fiat = available_fiat / (1 + self._fees.taker_fee)
        return available_fiat.quantize(self._min_fiat, ROUND_FLOOR)

    @property
    def max_fiat_for_maker(self) -> Decimal:
        """Get max available fiat for a 'maker' order"""
        available_fiat = self._balance.available_fiat_balance
        available_fiat = available_fiat / (1 + self._fees.maker_fee)
        return available_fiat.quantize(self._min_fiat, ROUND_FLOOR)

    @property
    def current_equity(self) -> Decimal:
        """Get current equity."""
        fiat_balance = self._balance.fiat_balance
        crypto_balance = self._balance.crypto_balance
        market_price = self._current_price
        equity = fiat_balance + crypto_balance * market_price
        return equity.quantize(self._min_fiat, ROUND_FLOOR)

    def iter_orders(self) -> t.Iterator[OrderInfo]:
        """Get orders iterator."""
        for order_id, order in self._orders:
            yield OrderInfo(order_id, order) 

    def get_orders(self) -> t.List[OrderInfo]:
        """Get orders list."""
        return list(self.iter_orders())

    def iter_trades(self) -> t.Iterator[TradeInfo]:
        """Get trades iterator."""
        return iter(self._trades)

    def get_trades(self) -> t.List[TradeInfo]:
        """Get trades list."""
        return list(self._trades)

    def submit_market_order(
                self, 
                options: MarketOrderOptions) -> MarketOrderInfo:
        """Submit market order."""
        order = self._create_market_order(options)
        order_id = self._orders.add_market_order(order)
        return MarketOrderInfo(order_id, order)

    def submit_limit_order(
                self, 
                options: LimitOrderOptions) -> LimitOrderInfo:
        """Submit limit order."""
        order = self._create_limit_order(options)
        order_id = self._orders.add_limit_order(order)
        strategy_orders = self._orders.get_linked_orders(order_id)
        return LimitOrderInfo(order_id, order, strategy_orders)

    def submit_take_profit_order(
                self, 
                order_side: OrderSide, 
                options: TakeProfitOptions) -> TakeProfitInfo:
        """Submit Take Profit order."""
        order = self._create_take_profit(order_side, options)
        order_id = self._orders.add_take_profit_order(order)
        return TakeProfitInfo(order_id, order)

    def submit_stop_loss_order(
                self, 
                order_side: OrderSide, 
                options: StopLossOptions) -> StopLossInfo:
        """Submit Stop Loss order."""
        order = self._create_stop_loss(order_side, options)
        order_id = self._orders.add_stop_loss_order(order)
        return StopLossInfo(order_id, order)

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

    def _add_trade(self, order_id: int, order: Order) -> None:
        """Add new trade."""
        trade_id = next(self._trades_counter)
        order_info = OrderInfo(order_id, order)
        balance = self._balance.fiat_balance
        self._trades.append(TradeInfo(trade_id, order_info, balance))

    def _submit_linked_take_profit(self, 
                                   order_side: OrderSide,
                                   options: TakeProfitOptions,
                                   limit_order_id: int,
                                   limit_order: LimitOrder) -> None:
        """Submit new linked TP from limit order."""
        order = self._create_linked_take_profit(order_side, options, limit_order)
        self._orders.add_linked_take_profit_order(order, limit_order_id)

    def _submit_linked_stop_loss(self, 
                                 order_side: OrderSide,
                                 options: StopLossOptions, 
                                 limit_order_id: int,
                                 limit_order: LimitOrder) -> None:
        """Submit new linked SL from limit order."""
        order = self._create_linked_stop_loss(order_side, options, limit_order)
        self._orders.add_linked_stop_loss_order(order, limit_order_id)

    def _create_take_profit(self, 
                            order_side: OrderSide,
                            options: TakeProfitOptions) -> TakeProfitOrder:
        """
        Initialize Take Profit order and acquire amount for execution.

        Acquired amount can be shared with other TP/SL orders.
        Should new TP/SL be posted, it can then acquire funds
        from the shared position without modifying the balance.
        """
        validate_take_profit_options(options)
        amount = Decimal('NaN')
        # Acquire fiat position
        if order_side is OrderSide.BUY:
            # Calculate total_price
            total_price = Decimal('NaN')
            if options.amount:
                amount = options.amount
                total_price = self._fees.estimate_maker_price(amount)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                amount = self.max_fiat_for_maker * percentage_rate
                total_price = self._fees.estimate_maker_price(amount)
            # Acquire from position or hold
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

        # Acquire crypto position
        elif order_side is OrderSide.SELL:
            # Estimate amount
            amount = Decimal('NaN')
            if options.amount:
                amount = options.amount
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_crypto = self.balance.available_crypto_balance
                amount = max_crypto * percentage_rate
            # Acquire from position or hold
            if amount <= self._balance.available_crypto_balance:
                # If total amount fits, hold funds and 
                # make it shared for other TP/SL 
                self._balance.hold_crypto(amount)
                self._shared_sell_position += amount 
            else:
                # Acquire only insufficient
                hold_amount = amount - self._shared_sell_position
                self._balance.hold_crypto(hold_amount)
            self._aggregated_sell_position += amount
        else:
            raise OrderSubmissionError()    # Invalid order side ??
        # Store order and return info
        return TakeProfitOrder(order_side,
                               amount=amount,
                               trigger_price=options.trigger_price,
                               order_price=options.order_price,
                               min_fiat=self._min_fiat, 
                               min_crypto=self._min_crypto, 
                               date_created=self._current_time)

    def _create_stop_loss(self, 
                          order_side: OrderSide, 
                          options: StopLossOptions) -> StopLossOrder:
        """
        Initialize Stop Loss order and acquire amount for execution.

        Acquired amount can be shared with other TP/SL orders.
        Should new TP/SL be posted, it can then acquire funds
        from the shared position without modifying the balance.
        """
        validate_stop_loss_options(options)
        amount = Decimal('NaN')
        # Acquire fiat position
        if order_side is OrderSide.BUY:
            # Calculate total_price
            total_price = Decimal('NaN')

            if options.amount:
                amount = options.amount
                total_price = self._fees.estimate_maker_price(amount)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                amount = self.max_fiat_for_maker * percentage_rate
                total_price = self._fees.estimate_maker_price(amount)
            # Acquire from position or hold
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

        # Acquire crypto position
        elif order_side is OrderSide.SELL:
            # Estimate amount
            amount = Decimal('NaN')

            if options.amount:
                amount = options.amount
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_crypto = self.balance.available_crypto_balance
                amount = max_crypto * percentage_rate
            # Acquire from position or hold
            if amount <= self._balance.available_crypto_balance:
                # If total amount fits, hold funds and 
                # make it shared for other TP/SL 
                self._balance.hold_crypto(amount)
                self._shared_sell_position += amount 
            else:
                # Acquire only insufficient
                hold_amount = amount - self._shared_sell_position
                self._balance.hold_crypto(hold_amount)
            self._aggregated_sell_position += amount
        else:
            raise OrderSubmissionError()    # Invalid order side
        # Store order and return info
        return StopLossOrder(order_side,
                             amount=amount,
                             trigger_price=options.trigger_price,
                             order_price=options.order_price,
                             min_fiat=self._min_fiat, 
                             min_crypto=self._min_crypto, 
                             date_created=self._current_time)

    def _create_linked_take_profit(
                self, 
                order_side: OrderSide,
                options: TakeProfitOptions,
                limit_order: LimitOrder) -> TakeProfitOrder:
        """
        Initialize Take Profit order and acquire amount for execution.

        Acquired amount can be shared with other TP/SL orders.
        Should new TP/SL be posted, it can then acquire funds
        from the shared position without modifying the balance.
        """
        validate_take_profit_options(options)
        amount = Decimal('NaN')
        # Acquire fiat position
        if order_side is OrderSide.BUY:
            # Calculate total_price
            total_price = Decimal('NaN')
            if options.amount:
                amount = options.amount
                total_price = self._fees.estimate_maker_price(amount)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_fiat = limit_order.amount * limit_order.fill_price
                max_fiat = max_fiat.quantize(self._min_fiat)
                amount = max_fiat * percentage_rate
                total_price = self._fees.estimate_maker_price(amount)
            # Acquire from position or hold
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

        # Acquire crypto position
        elif order_side is OrderSide.SELL:
            # Estimate amount
            amount = Decimal('NaN')
            if options.amount:
                amount = options.amount
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_crypto = limit_order.amount / limit_order.fill_price
                max_crypto = max_crypto.quantize(self._min_crypto)
                # max_crypto = self.balance.available_crypto_balance
                amount = max_crypto * percentage_rate
            # Acquire from position or hold
            if amount <= self._balance.available_crypto_balance:
                # If total amount fits, hold funds and 
                # make it shared for other TP/SL 
                self._balance.hold_crypto(amount)
                self._shared_sell_position += amount 
            else:
                # Acquire only insufficient
                hold_amount = amount - self._shared_sell_position
                self._balance.hold_crypto(hold_amount)
            self._aggregated_sell_position += amount
        else:
            raise OrderSubmissionError()    # Invalid order side ??
        # Store order and return info
        return TakeProfitOrder(order_side,
                               amount=amount,
                               trigger_price=options.trigger_price,
                               order_price=options.order_price,
                               min_fiat=self._min_fiat, 
                               min_crypto=self._min_crypto, 
                               date_created=self._current_time)

    def _create_linked_stop_loss(
                self, 
                order_side: OrderSide, 
                options: StopLossOptions,
                limit_order: LimitOrder) -> StopLossOrder:
        """
        Initialize Stop Loss order and acquire amount for execution.

        Acquired amount can be shared with other TP/SL orders.
        Should new TP/SL be posted, it can then acquire funds
        from the shared position without modifying the balance.
        """
        validate_stop_loss_options(options)
        amount = Decimal('NaN')
        # Acquire fiat position
        if order_side is OrderSide.BUY:
            # Calculate total_price
            total_price = Decimal('NaN')

            if options.amount:
                amount = options.amount
                total_price = self._fees.estimate_maker_price(amount)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_fiat = limit_order.amount * limit_order.fill_price
                max_fiat = max_fiat.quantize(self._min_fiat)
                amount = max_fiat * percentage_rate
                total_price = self._fees.estimate_maker_price(amount)
            # Acquire from position or hold
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

        # Acquire crypto position
        elif order_side is OrderSide.SELL:
            # Estimate amount
            amount = Decimal('NaN')

            if options.amount:
                amount = options.amount
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_crypto = limit_order.amount / limit_order.fill_price
                max_crypto = max_crypto.quantize(self._min_crypto)
                amount = max_crypto * percentage_rate
            # Acquire from position or hold
            if amount <= self._balance.available_crypto_balance:
                # If total amount fits, hold funds and 
                # make it shared for other TP/SL 
                self._balance.hold_crypto(amount)
                self._shared_sell_position += amount 
            else:
                # Acquire only insufficient
                hold_amount = amount - self._shared_sell_position
                self._balance.hold_crypto(hold_amount)
            self._aggregated_sell_position += amount
        else:
            raise OrderSubmissionError()    # Invalid order side
        # Store order and return info
        return StopLossOrder(order_side,
                             amount=amount,
                             trigger_price=options.trigger_price,
                             order_price=options.order_price,
                             min_fiat=self._min_fiat, 
                             min_crypto=self._min_crypto, 
                             date_created=self._current_time)

    def _create_market_order(
                self, 
                options: MarketOrderOptions) -> MarketOrder:
        """Initialize Market order and hold funds for execution."""
        validate_market_order_options(options)
        amount = Decimal('NaN')
        # Hold fiat
        if options.order_side is OrderSide.BUY:
            if options.amount:
                amount = options.amount
                total_price = self._fees.estimate_taker_price(amount)
                self._balance.hold_fiat(total_price)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                amount = self.max_fiat_for_taker * percentage_rate
                total_price = self._fees.estimate_taker_price(amount)
                self._balance.hold_fiat(total_price)
        # Hold crypto
        elif options.order_side is OrderSide.SELL:
            if options.amount:
                amount = options.amount
                self._balance.hold_crypto(options.amount)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_crypto = self.balance.available_crypto_balance
                amount = max_crypto * percentage_rate
                self._balance.hold_crypto(amount)
        else:
            raise OrderSubmissionError()    # Invalid order side
        # Store order and return info
        return MarketOrder(options.order_side, 
                           amount=amount, 
                           min_fiat=self._min_fiat, 
                           min_crypto=self._min_crypto, 
                           date_created=self._current_time)

    def _create_limit_order(
                self, 
                options: LimitOrderOptions) -> LimitOrder:
        """Initialize Limit order and hold funds for execution."""
        validate_limit_order_options(options)
        amount = Decimal('NaN')
        # Hold fiat
        if options.order_side is OrderSide.BUY:
            if options.amount:
                amount = options.amount
                total_price = self._fees.estimate_maker_price(amount)
                self._balance.hold_fiat(total_price)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                amount = self.max_fiat_for_maker * percentage_rate
                total_price = self._fees.estimate_maker_price(amount)
                self._balance.hold_fiat(total_price)
        # Hold crypto
        elif options.order_side is OrderSide.SELL:
            if options.amount:
                amount = options.amount
                self._balance.hold_crypto(options.amount)
            elif options.percentage_amount:
                percentage_rate = options.percentage_amount / 100
                max_crypto = self.balance.available_crypto_balance
                amount = max_crypto * percentage_rate
                self._balance.hold_crypto(amount)
        else:
            raise OrderSubmissionError()    # Invalid order side
        # Store order and return info
        return LimitOrder(options.order_side,
                          amount=amount,
                          order_price=options.order_price,
                          take_profit=options.take_profit,
                          stop_loss=options.stop_loss,
                          min_fiat=self._min_fiat, 
                          min_crypto=self._min_crypto, 
                          date_created=self._current_time)

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

    def _release_funds(self, order: t.Union[MarketOrder, LimitOrder]) -> None:
        """Increase funds available for trading."""
        if order.side is OrderSide.BUY:
            total_price = self._get_total_price(order)
            self._balance.release_fiat(total_price)
        elif order.side is OrderSide.SELL:
            self._balance.release_crypto(order.amount)

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

    def _get_maker_gain(self, 
                        order, 
                        fill_price: Decimal) -> t.Tuple[Decimal, Decimal]:
        """
        Estimate gain minus maker fee. Return gain and calculated fee.
        For SELL orders only.
        """
        total_amount = order.amount * fill_price
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
        self._current_price = candle.close
        # Execute all market orders
        self._execute_market_orders(candle.open)
        # Review orders with limited price
        # OPEN
        for order_id, order in self._orders.get_limit_orders():
            # Review strategy orders with open price
            if isinstance(order, StrategyOrder):
                if order.status is OrderStatus.CREATED:
                    if order.trigger_price == candle.open:
                        self._activate_strategy_order(order_id, order)
                elif order.status is OrderStatus.ACTIVATED:
                    if order.side is OrderSide.BUY:
                        if order.order_price >= candle.open:
                            self._execute_strategy_limit_order(order_id, order, candle.open)
                    elif order.side is OrderSide.SELL:
                        if order.order_price <= candle.open:
                            self._execute_strategy_limit_order(order_id, order, candle.open)
            # Review limit orders with open price
            elif isinstance(order, LimitOrder):
                if order.side is OrderSide.BUY:
                    if order.order_price >= candle.open:
                        self._execute_limit_order(order_id, order, candle.open)
                elif order.side is OrderSide.SELL:
                    if order.order_price <= candle.open:
                        self._execute_limit_order(order_id, order, candle.open)
        # HIGH, LOW
        for order_id, order in self._orders.get_limit_orders():
            # Review strategy order with HIGH, LOW prices
            if isinstance(order, StrategyOrder):
                if order.status is OrderStatus.CREATED:
                    if order.trigger_price >= candle.low and \
                            order.trigger_price <= candle.high:
                        self._activate_strategy_order(order_id, order)
                elif order.status is OrderStatus.ACTIVATED:
                    if order.side is OrderSide.BUY:
                        if order.order_price >= candle.low:
                            self._execute_strategy_limit_order(order_id, order, candle.low)
                    if order.side is OrderSide.SELL:
                        if order.order_price <= candle.high:
                            self._execute_strategy_limit_order(order_id, order, candle.high)
            # Review limit order with HIGH, LOW prices
            elif isinstance(order, LimitOrder):
                if order.side is OrderSide.BUY:
                    if order.order_price >= candle.low:
                        self._execute_limit_order(order_id, order, candle.low)
                elif order.side is OrderSide.SELL:
                    if order.order_price <= candle.high:
                        self._execute_limit_order(order_id, order, candle.high)

    def _execute_market_orders(self, market_price: Decimal) -> None:
        for order_id, order in self._orders.get_market_orders():
            if isinstance(order, MarketOrder):
                self._execute_market_order(order_id, order, market_price)
            elif isinstance(order, StrategyOrder):
                '''
                NOTE: since we're iterating over a copy, cancelled orders
                are still in the collection.
                '''
                if order.status is not OrderStatus.SYS_CANCELLED:
                    self._execute_strategy_market_order(order_id, 
                                                        order, market_price)
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
                             order: LimitOrder,
                             fill_price: Decimal) -> None:
        if order.side is OrderSide.BUY:
            price, fee = self._get_maker_price(order)
            order.trading_fee = fee
            self._balance.withdraw_fiat(price)
            self._balance.deposit_crypto(order.amount / fill_price)

        elif order.side is OrderSide.SELL:
            gain, fee = self._get_maker_gain(order, fill_price)
            order.trading_fee = fee
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(gain)

        order.status = OrderStatus.EXECUTED
        order.fill_price = fill_price
        order.date_updated = self._current_time
        self._orders.remove_limit_order(order_id)
        self._add_trade(order_id, order)
        # Cancel all TP/SL orders since position was modified
        self._cancel_strategy_orders()
        # Submit TP/SL orders, if any
        # Invert order side 
        order_side = OrderSide.BUY if order.side is OrderSide.SELL \
                        else OrderSide.SELL
        if order.take_profit_options:
            self._submit_linked_take_profit(order_side, 
                                            order.take_profit_options, 
                                            order_id, order)            
        if order.stop_loss_options:
            self._submit_linked_stop_loss(order_side, 
                                          order.stop_loss_options, 
                                          order_id, order)

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
                                      order: StrategyOrder,
                                      fill_price: Decimal) -> None:
        if order.side is OrderSide.BUY:
            price, fee = self._get_maker_price(order)
            order.trading_fee = fee
            self._balance.withdraw_fiat(price)
            self._balance.deposit_crypto(order.amount / fill_price)
            self._aggregated_buy_position -= price

        elif order.side is OrderSide.SELL:
            gain, fee = self._get_maker_gain(order, fill_price)
            order.trading_fee = fee
            self._balance.withdraw_crypto(order.amount)
            self._balance.deposit_fiat(gain)
            self._aggregated_sell_position -= order.amount 

        order.status = OrderStatus.EXECUTED
        order.fill_price = fill_price
        order.date_updated = self._current_time
        self._orders.remove_strategy_order(order_id)
        self._add_trade(order_id, order)
        # Cancel all other TP/SL orders since position was modified
        self._cancel_strategy_orders()