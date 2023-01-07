"""CSV export for backintime entities: stats, orders and trades."""
import csv
import typing as t
from decimal import Decimal
from datetime import datetime
from backintime.timeframes import Timeframes
from backintime.broker_proxy import Trade, OrderInfo
from .stats import Stats


def decimal_to_str(value: t.Optional[Decimal]) -> str:
    return "{0:.4f}".format(value) if value else str(Decimal('NaN'))


def datetime_to_str(value: datetime) -> str:
    """
    Represent datetime in ISO-8601 format 
    with date and time separated by space.
    """
    return value.isoformat(sep=' ')


class CSVStatsExporter:
    _stats_headers = (
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
        'Average Profit',
        'Profit/Loss ratio',
        'Win/Loss ratio',
        'Win rate',
        'Wins count',
        'Losses count',
        'Best deal (relative)',
        'Best deal (absolute)',
        'Worst deal (relative)',
        'Worst deal (absolute)',
    )

    def export(self, 
               filename: str,
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
            writer.writerow(self._stats_headers)
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
                    decimal_to_str(start_balance),
                    decimal_to_str(result_balance),
                    decimal_to_str(total_gain),
                    decimal_to_str(total_gain_percents),
                    # Stats item
                    item.algorithm,
                    decimal_to_str(item.avg_profit),
                    decimal_to_str(item.profit_loss_ratio),
                    decimal_to_str(item.win_loss_ratio),
                    decimal_to_str(item.win_rate),
                    item.wins_count,
                    item.losses_count,
                    decimal_to_str(item.best_deal_relative.relative_profit),
                    decimal_to_str(item.best_deal_absolute.absolute_profit),
                    decimal_to_str(item.worst_deal_relative.relative_profit),
                    decimal_to_str(item.worst_deal_absolute.absolute_profit)
                ])


class CSVOrdersExporter:
    _orders_fields = (
        "order_id",
        "order_type",
        "order_side",
        "amount",
        "date_created",
        "order_price",
        "status",
        "date_updated",
        "fill_price"
    )

    _orders_headers = {
        "order_id": "Order ID",
        "order_type": "Order Type",
        "order_side": "Side",
        "amount": "Amount",
        "date_created": "Date Created",
        "order_price": "Order Price",
        "status": "Status",
        "date_updated": "Date Updated",
        "fill_price": "Fill Price"
    }

    _field_serializers = {
        "amount": decimal_to_str,
        "fill_price": decimal_to_str,
        "order_price": decimal_to_str,
        "date_created": datetime_to_str,
        "date_updated": datetime_to_str
    }

    def export(self, 
               filename: str,
               delimiter: str,
               orders: t.Sequence[OrderInfo],
               exclude_fields: t.Iterable[str] = set()) -> None:
        """
        Export orders to CSV file. 
        Won't take effect if `orders` is an empty sequence.
        """
        if not len(orders):
            return

        fields = self._orders_fields
        fields = [ x for x in fields if not x in exclude_fields ]

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter,
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # Write headers
            writer.writerow(self._get_headers(fields))
            # Write content
            for order in orders:
                writer.writerow(self._serialize_order(order, fields))

    def _get_headers(self, fields: t.Set[str]) -> t.List[str]:
        """Get headers for orders."""
        return [ self._orders_headers[field] for field in fields ]

    def _serialize_order(self, 
                         order: OrderInfo, 
                         fields: t.Set[str]) -> t.List[str]:
        """Serialize order data to a list of strings."""
        return [
            self._serialize_field(order, field) 
                for field in fields 
        ]

    def _serialize_field(self, order: OrderInfo, field: str) -> str:
        serializer = self._field_serializers.get(field)
        value = self._get_field(order, field)
        return serializer(value) if serializer else str(value)

    def _get_field(self, order: OrderInfo, field: str) -> t.Any:
        """Get order attribute value by name."""
        return getattr(order, field)


class CSVTradesExporter:
    _trades_fields = (
        "order_id",
        "order_type",
        "order_side",
        "amount",
        "date_created",
        "order_price",
        "status",
        "date_updated",
        "fill_price",
        "result_balance"
    )

    _trades_headers = {
        "order_id": "Order ID",
        "order_type": "Order Type",
        "order_side": "Side",
        "amount": "Amount",
        "date_created": "Date Created",
        "order_price": "Order Price",
        "status": "Status",
        "date_updated": "Date Updated",
        "fill_price": "Fill Price",
        "result_balance": "Result Balance"
    }

    _field_serializers = {
        "amount": decimal_to_str,
        "fill_price": decimal_to_str,
        "order_price": decimal_to_str,
        "date_created": datetime_to_str,
        "date_updated": datetime_to_str
    }

    def export(self, 
               filename: str,
               delimiter: str,
               trades: t.Sequence[Trade],
               exclude_fields: t.Iterable[str] = set()) -> None:
        """
        Export trades to CSV file. 
        Won't take effect if `trades` is an empty sequence.
        """
        if not len(trades): 
            return

        fields = self._trades_fields
        fields = [ x for x in fields if not x in exclude_fields ]

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter,
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # Write headers
            writer.writerow(self._get_headers(fields))
            # Write content
            for trade in trades:
                writer.writerow(self._serialize_trade(trade, fields))

    def _get_headers(self, fields: t.Iterable[str]) -> t.List[str]:
        """Get headers for trades."""
        return [ self._trades_headers[field] for field in fields ]

    def _serialize_trade(self, 
                         trade: Trade, 
                         fields: t.Iterable[str]) -> t.List[str]:
        """Serialize trade data to a list of strings."""
        return [
            self._serialize_field(trade, field)
                for field in fields 
        ]

    def _serialize_field(self, trade: Trade, field: str) -> str:
        serializer = self._field_serializers.get(field)
        value = self._get_field(trade, field)
        return serializer(value) if serializer else str(value)

    def _get_field(self, trade: Trade, field: str) -> t.Any:
        """Get trade attribute value by name."""
        try:
            return getattr(trade, field) 
        except AttributeError:
            return getattr(trade.order, field)

# Helpers
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
    CSVStatsExporter().export(filename, delimiter, strategy_title,
                              date, data_title, data_timeframe, 
                              data_symbol, data_since, data_until, 
                              start_balance, result_balance, 
                              total_gain, total_gain_percents, stats)


def export_orders(filename: str,
                  delimiter: str,
                  orders: t.Sequence[OrderInfo],
                  exclude_fields: t.Iterable[str] = set()) -> None:
    """
    Export orders to CSV file.
    Won't take effect if `orders` is empty.
    """
    CSVOrdersExporter().export(filename, delimiter, orders, exclude_fields)


def export_trades(filename: str,
                  delimiter: str,
                  trades: t.Sequence[Trade],
                  exclude_fields: t.Iterable[str] = set()) -> None:
    """
    Export trades to CSV file.
    Won't take effect if `trades` is empty.
    """
    CSVTradesExporter().export(filename, delimiter, trades, exclude_fields)
