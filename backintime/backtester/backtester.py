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
    """
    Backtester is used to test a strategy (instance of :class:`TradingStrategy`)
    with market data (instance of :class:`CandlesProvider`),
    and then report results

    Override _fees to change trade fees. By default 0.1%
        is used for both maker and taker orders

    Override _broker_t to change default broker class
    """
    _fees = Fees(0.001, 0.001)
    _broker_t = Broker

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
        """Start backtesting, getting candles from `since` date and up to:
            a) if self._market_data is instance of TimeframeDump
                - read until the end of file
            b) get candles until current date otherwise

        :param since:
            string in ISO-8601 format (yyyy-mm-dd)
        :param start_money:
            initial funds for the test
        """
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
        """ Return results of the last run """
        return BacktestingResults(
            self._broker.positions(),
            self._start_date,
            self._end_date
        )
