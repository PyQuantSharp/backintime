"""CSV export for backintime entities: stats, orders and trades."""
import csv
import typing as t
from decimal import Decimal
from datetime import datetime
from backintime.timeframes import Timeframes
from backintime.broker.base import TradeInfo, OrderInfo
from .stats import Stats


def decimal_to_str(value: Decimal) -> str:
    """Covert decimal value to str with 4fp precision."""
    return str(value.quantize(Decimal('0.0001'))) if not value.is_nan() else ''


def datetime_to_str(value: datetime) -> str:
    """
    Represent datetime in ISO-8601 format 
    with date and time separated by space.
    """
    return value.isoformat(sep=' ')


def export_stats(filename: str,
                 delimiter: str,
                 strategy_title: str,
                 date: datetime,
                 data_title: str,
                 data_timeframe: Timeframes,
                 data_symbol: str,
                 data_since: datetime,
                 data_until: datetime,
                 start_balance: Decimal,
                 result_balance: Decimal,
                 total_gain: Decimal,
                 total_gain_percents: Decimal,
                 stats: t.Iterable[Stats]) -> None:
    """Export stats to CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # Write headers
        writer.writerow([
            'Strategy Title',
            'Date',
            'Data Provider',
            'Timeframe',
            'Symbol',
            'Since',
            'Until',
            'Start Balance',
            'Result Balance',
            'Total gain',
            'Total gain (%)',
            'Profit/Loss Algorithm',
            'Profit/Loss ratio',
            'Profit Factor',
            'Win/Loss ratio',
            'Win rate',
            'Wins count',
            'Losses count',
            'Average Profit (all trades)',
            'Average Profit (all trades), %',
            'Average Profit (profit-making trades)',
            'Average Profit (profit-making trades), %',
            'Average Loss (loss-making trades)',
            'Average Loss (loss-making trades), %',
            'Best deal (relative)',
            'Best deal (absolute)',
            'Worst deal (relative)',
            'Worst deal (absolute)',
        ])
        # Write content
        for item in stats:
            writer.writerow([
                # Args
                strategy_title,
                datetime_to_str(date),
                data_title,
                data_timeframe,
                data_symbol,
                datetime_to_str(data_since),
                datetime_to_str(data_until),
                start_balance,
                result_balance,
                total_gain,
                total_gain_percents,
                # Stats item
                item.algorithm,
                decimal_to_str(item.profit_loss_ratio),
                decimal_to_str(item.profit_factor),
                decimal_to_str(item.win_loss_ratio),
                decimal_to_str(item.win_rate),
                item.wins_count,
                item.losses_count,
                decimal_to_str(item.average_profit_all),
                decimal_to_str(item.average_profit_all_percents),
                decimal_to_str(item.average_profit),
                decimal_to_str(item.average_profit_percents),
                decimal_to_str(item.average_loss),
                decimal_to_str(item.average_loss_percents),
                decimal_to_str(item.best_deal_relative.relative_profit),
                decimal_to_str(item.best_deal_absolute.absolute_profit),
                decimal_to_str(item.worst_deal_relative.relative_profit),
                decimal_to_str(item.worst_deal_absolute.absolute_profit)
            ])


def export_orders(filename: str,
                  delimiter: str,
                  orders: t.Sequence[OrderInfo]) -> None:
    """
    Export orders to CSV file.
    Won't take effect if `orders` is empty.
    """
    if not len(orders): 
        return

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # Write headers
        writer.writerow([
            "Order ID",
            "Order Type",
            "Side",
            "Amount",
            "Date Created",
            "Order Price",
            "Status",
            "Date Updated",
            "Fill Price",
            "Trading Fee"
        ])
        # Write content
        for order in orders:
            writer.writerow([
                order.order_id,
                order.order_type,
                order.order_side,
                order.amount,
                datetime_to_str(order.date_created),
                order.order_price,
                order.status,
                datetime_to_str(order.date_updated),
                order.fill_price,
                order.trading_fee,
            ])


def export_trades(filename: str,
                  delimiter: str,
                  trades: t.Sequence[TradeInfo]) -> None:
    """
    Export trades to CSV file.
    Won't take effect if `trades` is empty.
    """
    if not len(trades): 
        return

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # Write headers
        writer.writerow([
            "Order ID",
            "Order Type",
            "Side",
            "Amount",
            "Date Created",
            "Order Price",
            "Status",
            "Date Updated",
            "Fill Price",
            "Trading Fee",
            "Result Balance"
        ])
        # Write content
        for trade in trades:
            writer.writerow([
                trade.order.order_id,
                trade.order.order_type,
                trade.order.order_side,
                trade.order.amount,
                datetime_to_str(trade.order.date_created),
                trade.order.order_price,
                trade.order.status,
                datetime_to_str(trade.order.date_updated),
                trade.order.fill_price,
                trade.order.trading_fee,
                trade.result_balance
            ])
