from typing import Type

from ..fees import Fees
from ..trading_strategy import TradingStrategy
from ..broker import Broker
from ..candles_providers import CandlesProvider
from ..candle_properties import CandleProperties
from ..timeframes import Timeframes
from .backtesting_results import BacktestingResults

import datetime


class Backtester:

    _fees = Fees(0.001, 0.001)
    _broker_t = Broker
    # fees --> broker_t(market_data, money, fees)
    def __init__(
            self,
            strategy_class: Type[TradingStrategy],
            market_data: CandlesProvider
            ):
        self._strategy_t = strategy_class
        self._market_data = market_data
        self._broker = None
        self._start_date = None
        self._end_date = None
        self.fees = self._fees

    def run_test(self, since: str, start_money: float) -> None:
        self._broker = self._broker_t(self._market_data, start_money, self._fees)
        since = datetime.datetime.fromisoformat(since)
        self._start_date = since
        self._market_data.set_start_date(since)

        ts = self._strategy_t(self._market_data, self._broker)

        try:
            while True:
                ts.next()
        except Exception as e:
            if isinstance(e, StopIteration):
                pass
            else:
                print(e)
                raise e
            '''
            elif isinstance(e, UnsufficientFunds):
                print(e)
            '''
        self._end_date = self._market_data.current_date()

    def results(self) -> BacktestingResults:
        return BacktestingResults(
            self._broker.positions(),
            self._start_date,
            self._end_date
        )
