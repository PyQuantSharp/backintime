import typing as t
from dataclasses import dataclass
from collections import deque
from decimal import Decimal, DivisionByZero
from backintime.broker_proxy import Trade
from backintime.broker.orders import OrderSide


@dataclass
class TradeProfit:
    trade_id: int
    order_id: int
    relative_profit: Decimal
    absolute_profit: Decimal


def _repr_profit(trade_profit: TradeProfit, percents_first=True) -> str:
    """
    Utility to represent `TradeProfit` object with control over
    the order of fields, for instance:
        Best deal (relative change): +14% (+5k absoulte) Trade#10 Order#15
        Best deal (absolute change): +20k (+10% relative) Trade#11 Order#20
    """
    if trade_profit is None:
        return repr(None)
    if percents_first:
        return (f"{trade_profit.relative_profit:+.2f}% "
                f"({trade_profit.absolute_profit:+.2f} absolute) "
                f"Trade#{trade_profit.trade_id} "
                f"Order#{trade_profit.order_id}")
    else:
        return (f"{trade_profit.absolute_profit:+.2f} "
                f"({trade_profit.relative_profit:+.2f}% relative) "
                f"Trade#{trade_profit.trade_id} "
                f"Order#{trade_profit.order_id}")


def _repr_percents(value: Decimal) -> str:
    """Represent decimal value in percents format."""
    return f"{value:+.2f}%" if not value.is_nan() else str(value)


@dataclass
class Stats:
    algorithm: str
    trades_profit: list
    profit_loss_ratio: Decimal = Decimal('NaN')
    profit_factor: Decimal = Decimal('NaN')
    win_rate: Decimal = Decimal('NaN')
    win_loss_ratio: Decimal = Decimal('NaN')
    wins_count: int = 0
    losses_count: int = 0
    average_profit_all: Decimal = Decimal('NaN')
    average_profit_all_percents: Decimal = Decimal('NaN')
    average_profit: Decimal = Decimal('NaN')
    average_profit_percents: Decimal = Decimal('NaN')
    average_loss: Decimal = Decimal('NaN')
    average_loss_percents: Decimal = Decimal('NaN')
    best_deal_relative: t.Optional[TradeProfit] = None
    best_deal_absolute: t.Optional[TradeProfit] = None
    worst_deal_relative: t.Optional[TradeProfit] = None
    worst_deal_absolute: t.Optional[TradeProfit] = None

    def __repr__(self) -> str:
        best_deal_rel = _repr_profit(self.best_deal_relative)
        best_deal_abs = _repr_profit(self.best_deal_absolute, False)
        worst_deal_rel = _repr_profit(self.worst_deal_relative)
        worst_deal_abs = _repr_profit(self.worst_deal_absolute, False)

        win_rate = f"{self.win_rate:.2f}%" if not self.win_rate.is_nan() \
                    else str(self.win_rate) 
        avg_profit_percents = _repr_percents(self.average_profit_percents)
        avg_loss_percents = _repr_percents(self.average_loss_percents)
        avg_profit_all_percents = _repr_percents(self.average_profit_all_percents)

        return (f"Profit/Loss algorithm: {self.algorithm}\n\n"
                f"Profit/Loss:\t{self.profit_loss_ratio:.2f}\n"
                f"Profit Factor:\t{self.profit_factor:.2f}\n"
                f"Win rate:\t{win_rate}\n"
                f"Win/Loss:\t{self.win_loss_ratio:.2f}\n"
                f"Wins count:\t{self.wins_count}\n"
                f"Losses count:\t{self.losses_count}\n\n"
                f"Avg. Profit (all trades): {self.average_profit_all:.2f}\n"
                f"Avg. Profit (all trades), %: {avg_profit_all_percents}\n"
                f"Avg. Profit (profit-making trades): {self.average_profit:.2f}\n"
                f"Avg. Profit (profit-making trades), %: {avg_profit_percents}\n"
                f"Avg. Loss (loss-making trades): {self.average_loss:.2f}\n"
                f"Avg. Loss (loss-making trades), %: {avg_loss_percents}\n\n"
                f"Best deal (relative change): {best_deal_rel}\n"
                f"Best deal (absolute change): {best_deal_abs}\n"
                f"Worst deal (relative change): {worst_deal_rel}\n"
                f"Worst deal (absolute change): {worst_deal_abs}\n")


class InvalidSellAmount(Exception):
    def __init__(self, sell_amount, position):
        message = (f"Can't sell more than was bought. "
                   f"Sell amount: {sell_amount}, position: {position}")
        super().__init__(message)


class UnexpectedProfitLossAlgorithm(Exception):
    def __init__(self, algorithm_name: str, supported: t.Iterable[str]):
        message = (f"Unexpected algorithm `{algorithm_name}`. "
                   f"Supported algorithms are: {supported}.")
        super().__init__(message)


def _validate_sell_amount(sell_amount: Decimal, position: Decimal) -> None:
    if sell_amount > position:
        raise InvalidSellAmount(sell_amount, position)


def get_stats(algorithm: str, trades: t.Sequence[Trade]) -> Stats:
    """
    Get stats such as Win Rate, Profit/Loss, Average Profit, etc.
    Supports estimation in FIFO (First-In-First-Out), 
    LIFO (Last-In-First-Out) or AVCO (Average Cost) algorithms.
    The algorithm name specifies the order in which BUYs
    must be considered to estimate profit or loss.

    All these algorithms produce the same result if SELL
    order always follows only one BUY with the same amount.

    Return stats with default values for empty trades list 
    or for trades list without sells.
    """
    if algorithm == 'FIFO':
        trades_profit = fifo_profit(trades)
    elif algorithm == 'LIFO':
        trades_profit = lifo_profit(trades)
    elif algorithm == 'AVCO': 
        trades_profit = avco_profit(trades)
    else:
        supported = ('FIFO', 'LIFO', 'AVCO')
        raise UnexpectedProfitLossAlgorithm(algorithm, supported)

    stats = Stats(algorithm=algorithm, trades_profit=trades_profit)
    if not len(trades_profit):
        return stats

    wins_count = 0
    losses_count = 0
    total_gain = 0
    total_loss = 0

    acc_percents = 0
    acc_loss_percents = 0
    acc_profit_percents = 0

    best_absolute = worst_absolute = trades_profit[0]
    best_relative = worst_relative = trades_profit[0]
    # It's more accurate to calculate all we need in a single loop
    for profit in trades_profit:
        if profit.absolute_profit > 0:
            wins_count += 1
            total_gain += profit.absolute_profit
            acc_profit_percents += profit.relative_profit

        elif profit.absolute_profit < 0:
            losses_count += 1 
            total_loss += abs(profit.absolute_profit)
            acc_loss_percents += abs(profit.relative_profit)

        acc_percents += profit.relative_profit
        best_relative = max(profit, best_relative,
                            key=lambda trade: trade.relative_profit)
        best_absolute = max(profit, best_absolute, 
                            key=lambda trade: trade.absolute_profit)
        worst_relative = min(profit, worst_relative,
                             key=lambda trade: trade.relative_profit)
        worst_absolute = min(profit, worst_absolute,
                             key=lambda trade: trade.absolute_profit)

    trades_count = len(trades)
    sell_trades_count = len(trades_profit)

    try:
        stats.wins_count = wins_count
        stats.losses_count = losses_count
        stats.best_deal_absolute = best_absolute
        stats.best_deal_relative = best_relative
        stats.worst_deal_absolute = worst_absolute
        stats.worst_deal_relative = worst_relative
        average_profit = total_gain/wins_count
        stats.average_profit = average_profit
        stats.average_profit_percents = acc_profit_percents / wins_count
        average_loss = total_loss/losses_count
        stats.average_loss = -average_loss
        stats.average_loss_percents = - (acc_loss_percents / losses_count)
        stats.average_profit_all = (total_gain - total_loss) / sell_trades_count
        stats.average_profit_all_percents = acc_percents / sell_trades_count
        stats.profit_loss_ratio = average_profit/average_loss
        stats.profit_factor = total_gain/total_loss
        stats.win_loss_ratio = Decimal(wins_count/losses_count)
        stats.win_rate = Decimal(wins_count/(sell_trades_count/100))

    except (ZeroDivisionError, DivisionByZero):
        # Just ignore and use defaults
        pass

    return stats


class _PositionItem:    # BUY orders only
    def __init__(self, trade: Trade):
        self.amount = trade.order.amount
        # TODO: consider passing quantize precision to ctor
        quantity = trade.order.amount / trade.order.fill_price
        self.quantity = quantity.quantize(Decimal('0.00000001'))
        self.fill_price = trade.order.fill_price
        self.trading_fee = trade.order.trading_fee
        self._remaining_fee = trade.order.trading_fee
        self._remaining_quantity = self.quantity

    @property
    def remaining_quantity(self):
        return self._remaining_quantity

    @remaining_quantity.setter
    def remaining_quantity(self, value):
        self._remaining_quantity = value

    @property
    def remaining_fee(self):
        return self._remaining_fee

    @remaining_fee.setter
    def remaining_fee(self, value):
        self._remaining_fee = value.quantize(Decimal('0.01'))

    def __repr__(self) -> str:
        return (f"PositionItem(amount={self.amount}, "
                f"fill_price={self.fill_price}, "
                f"remaining_quantity={self.remaining_quantity}, "
                f"remaining_fee={self.remaining_fee})\n")


def _get_gain(trade: Trade) -> Decimal: # SELL orders only
    total_amount = trade.order.amount * trade.order.fill_price
    return total_amount - trade.order.trading_fee 


def _estimate_trade_profit(trade: Trade, position: Decimal) -> TradeProfit:
    trade_gain = _get_gain(trade)
    absolute_profit = trade_gain - position
    relative_profit = trade_gain/(position/100) - 100
    return TradeProfit(absolute_profit=absolute_profit,
                       relative_profit=relative_profit,
                       trade_id=trade.trade_id, 
                       order_id=trade.order.order_id)


def fifo_profit(trades: t.Iterable[Trade]) -> t.List[TradeProfit]:
    """FIFO Profit/Loss calculation algorithm."""
    trades_profit: t.List[TradeProfit] = []
    position = deque()

    for trade in trades:
        if trade.order.order_side is OrderSide.BUY:
            position.append(_PositionItem(trade))
        else:   # SELL
            position_quantity = sum(x.remaining_quantity for x in position)
            sell_quantity = trade.order.amount
            _validate_sell_amount(sell_quantity, position_quantity)
            position_price = 0

            while len(position) and position[0].remaining_quantity <= sell_quantity:
                item = position.popleft()
                sell_quantity -= item.remaining_quantity
                amount = item.remaining_quantity * item.fill_price
                position_price += amount + item.remaining_fee

            if sell_quantity:
                item = position[0]
                quantity_ratio = sell_quantity/item.remaining_quantity
                partial_fee =  quantity_ratio * item.trading_fee
                partial_amount = sell_quantity * item.fill_price

                item.remaining_quantity -= sell_quantity
                item.remaining_fee -= partial_fee

                position_price += partial_amount + partial_fee

            trade_profit = _estimate_trade_profit(trade, position_price)
            trades_profit.append(trade_profit)
    return trades_profit


def lifo_profit(trades: t.Iterable[Trade]) -> t.List[TradeProfit]:
    """LIFO Profit/Loss calculation algorithm."""
    trades_profit: t.List[TradeProfit] = []
    position = deque()

    for trade in trades:
        if trade.order.order_side is OrderSide.BUY:
            position.append(_PositionItem(trade))
        else:   # SELL
            position_quantity = sum(x.remaining_quantity for x in position)
            sell_quantity = trade.order.amount
            _validate_sell_amount(sell_quantity, position_quantity)
            position_price = 0

            while len(position) and position[-1].remaining_quantity <= sell_quantity:
                item = position.pop()
                sell_quantity -= item.remaining_quantity
                amount = item.remaining_quantity * item.fill_price
                position_price += amount + item.remaining_fee

            if sell_quantity:
                item = position[-1]
                quantity_ratio = sell_quantity/item.remaining_quantity
                partial_fee =  quantity_ratio * item.trading_fee
                partial_amount = sell_quantity * item.fill_price

                item.remaining_quantity -= sell_quantity
                item.remaining_fee -= partial_fee

                position_price += partial_amount + partial_fee

            trade_profit = _estimate_trade_profit(trade, position_price)
            trades_profit.append(trade_profit)
    return trades_profit


def avco_profit(trades: t.Iterable[Trade]) -> t.List[TradeProfit]:
    """AVCO Profit/Loss calculation algorithm."""
    trades_profit: t.List[TradeProfit] = []
    position = []

    for trade in trades:
        if trade.order.order_side is OrderSide.BUY:
            position.append(_PositionItem(trade))
        else:   # SELL
            position_quantity = sum(x.remaining_quantity for x in position)
            sell_quantity = trade.order.amount
            _validate_sell_amount(sell_quantity, position_quantity)
            position_price = 0

            while sell_quantity:
                '''
                NOTE: the following line never raises 
                `ZeroDivisionError`, since by the time when 
                len(position) is 0, `sell_quantity` is 0 as well, 
                which is exactly the condition to break `while` loop.

                This is implied by the `_validate_sell_amount`: 
                when all BUYs are consumed and removed, there is 
                nothing to sell remains.

                So, this line won't execute with dangerous 
                values either way.
                '''
                even = sell_quantity/len(position) 

                for item in position.copy():
                    if item.remaining_quantity <= even:
                        quantity = item.remaining_quantity
                        fill_price = item.fill_price
                        remaining_fee = item.remaining_fee
                        amount = quantity * fill_price

                        position_price += amount + remaining_fee
                        sell_quantity -= quantity
                        position.remove(item)
                        if len(position):   # prevent zero division
                            even = sell_quantity/len(position)
                    else:
                        quantity_ratio = even/item.remaining_quantity
                        partial_fee = quantity_ratio * item.remaining_fee
                        partial_amount = even * item.fill_price
                        position_price += partial_amount + partial_fee

                        sell_quantity -= even
                        item.remaining_quantity -= even
                        item.remaining_fee -= partial_fee

            trade_profit = _estimate_trade_profit(trade, position_price)
            trades_profit.append(trade_profit)
    return trades_profit
