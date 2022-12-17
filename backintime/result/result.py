import typing as t
from datetime import datetime, timezone
from decimal import Decimal
from backintime.data.data_provider import DataProvider
from backintime.broker_proxy import Trade, OrderInfo
from .stats import Stats, TradeProfit, get_stats


class BacktestingStats:
    def __init__(self, 
                 strategy_title: str,
                 data_provider: DataProvider,
                 date: datetime,
                 stats: Stats):
        self._strategy_title = strategy_title
        self._data_title = data_provider.title
        self._data_timeframe = data_provider.timeframe
        self._symbol = data_provider.symbol
        self._date = date
        self._stats = stats

    @property
    def strategy_title(self) -> str:
        return self._strategy_title

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def algorithm(self) -> str:
        return self._stats.algorithm

    @property
    def average_profit(self) -> Decimal:
        return self._stats.average_profit

    @property
    def profit_loss_ratio(self) -> Decimal:
        return self._stats.profit_loss_ratio

    @property
    def win_loss_ratio(self) -> Decimal:
        return self._stats.win_loss_ratio

    @property
    def win_rate(self) -> Decimal:
        return self._stats.win_rate

    @property
    def wins_count(self) -> int:
        return self._stats.wins_count

    @property
    def losses_count(self) -> int:
        return self._stats.losses_count

    @property
    def best_deal_relative(self) -> t.Optional[TradeProfit]:
        return self._stats.best_deal_relative

    @property
    def best_deal_absolute(self) -> t.Optional[TradeProfit]:
        return self._stats.best_deal_absolute

    @property
    def worst_deal_relative(self) -> t.Optional[TradeProfit]:
        return self._stats.worst_deal_relative

    @property
    def worst_deal_absolute(self) -> t.Optional[TradeProfit]:
        return self._stats.worst_deal_absolute

    def __repr__(self) -> str:
        stars = f"\n{'*' * 50}\n"
        header = f"Backtesting stats {self._date}\n" # format?
        data_block = (f"{self._data_title}\n"
                      f"on {self._data_timeframe}\n"
                      f"traiding pair: {self._symbol}\n")

        return (f"{stars}{header}{data_block}"
                f"Strategy title: {self._strategy_title}\n"
                f"{repr(self._stats)}"
                f"{stars}")


class BacktestingResult:

    _trades_fields = {
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
    }

    _orders_fields = {
        "order_id",
        "order_type",
        "order_side",
        "amount",
        "date_created",
        "order_price",
        "status",
        "date_updated",
        "fill_price"
    }

    def __init__(self, 
                 strategy_title: str, 
                 data_provider: DataProvider,
                 start_balance: Decimal,
                 result_balance: Decimal,
                 trades: t.Sequence[Trade],
                 orders: t.Sequence[OrderInfo]):
        self._data_provider = data_provider
        self._data_title = data_provider.title
        self._data_timeframe = data_provider.timeframe
        self._symbol = data_provider.symbol
        self._strategy_title = strategy_title
        self._start_balance = start_balance
        self._result_balance = result_balance
        diff = result_balance - start_balance
        self._total_gain = diff
        self._total_gain_percents = diff/(start_balance/100)
        self._trades = trades
        self._orders = orders
        self._trades_count = len(trades)
        self._orders_count = len(orders)
        self._date = datetime.now(tz=timezone.utc)

    @property
    def strategy_title(self) -> str:
        return self._strategy_title

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def start_balance(self) -> Decimal:
        return self._start_balance

    @property
    def result_balance(self) -> Decimal:
        return self._result_balance

    @property
    def total_gain(self) -> Decimal:
        return self._total_gain

    @property
    def total_gain_percents(self):
        return self._total_gain_percents

    @property
    def trades_count(self) -> int:
        return self._trades_count

    @property
    def orders_count(self) -> int:
        return self._orders_count

    def get_stats(self, algorithm: str) -> BacktestingStats:
        return BacktestingStats(self._strategy_title, 
                                self._data_provider, 
                                self._date, 
                                get_stats(algorithm, self._trades))

    def export(self, filename: str) -> None:
        pass

    def export_stats(self, algorithm: str, filename: str, delimiter=';') -> None:
        """Export stats to CSV file."""
        pass

    def export_trades(self, 
                      filename: t.Optional[str]=None, 
                      exclude_fields: t.Optional[t.Set[str]]=set(),
                      delimiter=';') -> None:
        """Export trades to CSV file."""
        pass

    def export_orders(self, 
                      filename: t.Optional[str]=None,
                      exclude_fields: t.Optional[t.Set[str]]=set(),
                      delimiter=';') -> None:
        """Export orders to CSV file."""
        pass

    def __repr__(self) -> str:
        stars = f"\n{'*' * 50}\n"
        header = f"Backtesting result {self._date}\n" # format?
        data_block = (f"{self._data_title}\n"
                      f"on {self._data_timeframe}\n"
                      f"traiding pair: {self._symbol}\n")

        content = (f"Strategy title: {self.strategy_title}\n"
                   f"Start balance:\t\t{self.start_balance}\n"
                   f"Result balance: \t{self.result_balance}\n"
                   f"Total gain:\t\t{self.total_gain}\n"
                   f"Total gain percents:\t{self.total_gain_percents:.2f}%\n"
                   f"Trades count:\t{self.trades_count}\n"
                   f"Orders count:\t{self.orders_count}\n")

        return f"{stars}{header}{data_block}{content}{stars}"
