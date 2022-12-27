import typing as t
from dataclasses import dataclass
from collections import deque
from decimal import Decimal, DivisionByZero
from backintime.broker_proxy import Trade
from backintime.broker.orders import OrderSide


@dataclass
class TradeProfit:
    relative_profit: Decimal
    absolute_profit: Decimal
    trade_id: int
    order_id: int


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


@dataclass
class Stats:
    algorithm: str
    trades_profit: list
    avg_profit: t.Optional[Decimal]=Decimal('NaN')
    win_rate: t.Optional[Decimal]=Decimal('NaN')
    profit_loss_ratio: t.Optional[Decimal]=Decimal('NaN')
    win_loss_ratio: t.Optional[Decimal]=Decimal('NaN')
    wins_count: t.Optional[int]=0
    losses_count: t.Optional[int]=0
    best_deal_relative: t.Optional[TradeProfit]=None
    best_deal_absolute: t.Optional[TradeProfit]=None
    worst_deal_relative: t.Optional[TradeProfit]=None
    worst_deal_absolute: t.Optional[TradeProfit]=None

    def __repr__(self) -> str:
        best_deal_rel = _repr_profit(self.best_deal_relative)
        best_deal_abs = _repr_profit(self.best_deal_absolute, False)
        worst_deal_rel = _repr_profit(self.worst_deal_relative)
        worst_deal_abs = _repr_profit(self.worst_deal_absolute, False)

        return (f"Profit/Loss algorithm: {self.algorithm}\n\n"
                f"Avg. profit:\t{self.avg_profit:.2f}%\n"
                f"Profit/Loss:\t{self.profit_loss_ratio:.2f}\n"
                f"Win rate:\t{self.win_rate:.2f}%\n"
                f"Win/Loss:\t{self.win_loss_ratio:.2f}\n"
                f"Wins count:\t{self.wins_count}\n"
                f"Losses count:\t{self.losses_count}\n\n"
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
    # Return stats with default values for empty trades list 
    # or for trades list without sells.
    if algorithm == 'FIFO':
        trades_profit = _fifo_profit(trades)
    elif algorithm == 'LIFO':
        trades_profit = _lifo_profit(trades)
    elif algorithm == 'ACVO': 
        trades_profit = _acvo_profit(trades)
    else:
        supported = ('FIFO', 'LIFO', 'ACVO')
        raise UnexpectedProfitLossAlgorithm(algorithm, supported)

    if not len(trades_profit):
        return Stats(algorithm=algorithm, trades_profit=trades_profit)

    wins_count = 0
    losses_count = 0
    profit_sum = 0
    total_gain = 0
    total_loss = 0
    best_absolute = worst_absolute = trades_profit[0]
    best_relative = worst_relative = trades_profit[0]
    # It's more accurate to calculate all we need in a single loop
    for profit in trades_profit:
        if profit.absolute_profit > 0:
            wins_count += 1
            total_gain += profit.absolute_profit
        elif profit.absolute_profit < 0:
            losses_count += 1 
            total_loss += abs(profit.absolute_profit)

        profit_sum += profit.relative_profit
        best_relative = max(profit, best_relative,
                            key=lambda trade: trade.relative_profit)
        best_absolute = max(profit, best_absolute, 
                            key=lambda trade: trade.absolute_profit)
        worst_relative = min(profit, worst_relative,
                             key=lambda trade: trade.relative_profit)
        worst_absolute = min(profit, worst_absolute,
                             key=lambda trade: trade.absolute_profit)

    trades_count = len(trades)
    # Set defaults
    profit_loss_ratio = Decimal('NaN')
    win_loss_ratio = Decimal('NaN')

    try:
        avg_profit = total_gain/wins_count
        profit_loss_ratio = avg_profit/(total_loss/losses_count)
        win_loss_ratio = wins_count/losses_count
    except (ZeroDivisionError, DivisionByZero):
        # Just ignore and use defaults
        pass

    sell_trades_count = len(trades_profit)
    win_rate = wins_count/(sell_trades_count/100)
    avg_profit = profit_sum/sell_trades_count

    return Stats(algorithm=algorithm,
                 avg_profit=avg_profit,
                 win_rate=win_rate, 
                 profit_loss_ratio=profit_loss_ratio,
                 win_loss_ratio=win_loss_ratio,
                 wins_count=wins_count,
                 losses_count=losses_count,
                 best_deal_relative=best_relative,
                 best_deal_absolute=best_absolute,
                 worst_deal_relative=worst_relative,
                 worst_deal_absolute=worst_absolute,
                 trades_profit=trades_profit)


class _PositionItem:    # BUY orders only
    def __init__(self, trade: Trade):
        self.amount = trade.order.amount
        # TODO: consider passing quantize precision to ctor
        quantity = trade.order.amount / trade.order.fill_price
        self.quantity = quantity.quantize(Decimal('0.00000001'))
        self.fill_price = trade.order.fill_price
        self.trading_fee = trade.order.trading_fee


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


def _fifo_profit(trades: t.Iterable[Trade]) -> t.List[TradeProfit]:
    """FIFO Profit/Loss calculation algorithm."""
    trades_profit: t.List[TradeProfit] = []
    position = deque()

    for trade in trades:
        if trade.order.order_side is OrderSide.BUY:
            position.appendleft(_PositionItem(trade))
        else:   # SELL
            position_quantity = sum(x.quantity for x in position)
            sell_quantity = trade.order.amount
            _validate_sell_amount(sell_quantity, position_quantity)
            position_price = 0

            while len(position) and position[0].quantity <= sell_quantity:
                item = position.pop()
                sell_quantity -= item.quantity 
                position_price += item.amount + item.trading_fee
            if sell_quantity:
                item = position[0]
                item.quantity -= sell_quantity
                position_price += sell_quantity * item.fill_price + item.trading_fee

            trade_profit = _estimate_trade_profit(trade, position_price)
            trades_profit.append(trade_profit)
    return trades_profit


def _lifo_profit(trades: t.Iterable[Trade]) -> t.List[TradeProfit]:
    """LIFO Profit/Loss calculation algorithm."""
    trades_profit: t.List[TradeProfit] = []
    position = deque()

    for trade in trades:
        if trade.order.order_side is OrderSide.BUY:
            position.append(_PositionItem(trade))
        else:   # SELL
            position_quantity = sum(x.quantity for x in position)
            sell_quantity = trade.order.amount
            _validate_sell_amount(sell_quantity, position_quantity)
            position_price = 0

            while len(position) and position[-1].quantity <= sell_quantity:
                item = position.pop()
                sell_quantity -= item.quantity
                position_price += item.amount + item.trading_fee
            if sell_quantity:
                item = position[-1]
                item.quantity -= sell_quantity
                position_price += sell_quantity * item.fill_price + item.trading_fee

            trade_profit = _estimate_trade_profit(trade, position_price)
            trades_profit.append(trade_profit)
    return trades_profit


def _acvo_profit(trades: t.Iterable[Trade]) -> t.List[TradeProfit]:
    """ACVO Profit/Loss calculation algorithm."""
    trades_profit: t.List[TradeProfit] = []
    position = []

    for trade in trades:
        if trade.order.order_side is OrderSide.BUY:
            position.append(_PositionItem(trade))
        else:   # SELL
            position_quantity = sum(x.quantity for x in position)
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
                
                for position_trade in position.copy():
                    if position_trade.quantity <= even:
                        position_price += position_trade.amount + position_trade.trading_fee
                        sell_quantity -= position_trade.quantity
                        position.remove(position_trade)
                        if len(position):   # prevent zero division
                            even = sell_quantity/len(position)
                    else:
                        position_price += even * position_trade.fill_price + position_trade.trading_fee
                        sell_quantity -= even
                        position_trade.quantity -= even

            trade_profit = _estimate_trade_profit(trade, position_price)
            trades_profit.append(trade_profit)
    return trades_profit
