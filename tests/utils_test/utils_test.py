import os
import typing as t
from pytest import fixture
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from backintime.trading_strategy import TradingStrategy
from backintime.timeframes import Timeframes as tf
from backintime.data.csv import CSVCandlesFactory
from backintime.analyser.analyser import Analyser
from backintime.analyser.indicators.sma import sma_params as sma
from backintime.utils import (
    run_backtest,
    prefetch_values, 
    PREFETCH_SINCE, 
    PREFETCH_UNTIL,
    IncompatibleTimeframe
)


@fixture
def stumb_strategy() -> t.Type[TradingStrategy]:
    class MyStrategy(TradingStrategy):
        title = "Stumb strategy"
        indicators = { sma(tf.H4) }

        def tick(self):
            pass
   
    return MyStrategy


def test_prefetch_until(stumb_strategy):
    """
    Ensure that prefetching with `PREFETCH_UNTIL` option returns
    `AnalyserBuffer` with valid values, 
    using MA calculation as a criterion. 
    """
    dirname = os.path.dirname(__file__)
    test_file = os.path.join(dirname, "test_h4.csv")
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    until = datetime.fromisoformat("2021-12-01 00:00+00:00")
    expected_start_date = until
    expected_sma = Decimal('57311.97')
    expected_precision = Decimal('0.01')

    analyser_buffer, date = prefetch_values(stumb_strategy, candles, 
                                            PREFETCH_UNTIL, until)
    analyser = Analyser(analyser_buffer)

    sma = analyser.sma(tf.H4)[-1]
    sma_diff = (Decimal(sma) - expected_sma).copy_abs()
    sma_diff = sma_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert expected_start_date == date
    assert sma_diff <= expected_precision


def test_prefetch_since(stumb_strategy):
    """
    Ensure that prefetching with `PREFETCH_SINCE` option returns
    `AnalyserBuffer` with valid values, 
    using MA calculation as a criterion. 
    """
    dirname = os.path.dirname(__file__)
    test_file = os.path.join(dirname, "test_h4.csv")
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    since = datetime.fromisoformat("2021-11-29 12:00+00:00")
    expected_start_date = datetime.fromisoformat("2021-12-01 00:00+00:00")
    expected_sma = Decimal('57311.97')
    expected_precision = Decimal('0.01')

    analyser_buffer, date = prefetch_values(stumb_strategy, candles, 
                                            PREFETCH_SINCE, since)
    analyser = Analyser(analyser_buffer)

    sma = analyser.sma(tf.H4)[-1]
    sma_diff = (Decimal(sma) - expected_sma).copy_abs()
    sma_diff = sma_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert expected_start_date == date
    assert sma_diff <= expected_precision


def test_incompatible_timeframe(stumb_strategy):
    """
    Ensure that passing incompatible timeframe into `run_backtest` 
    will raise `IncompatibleTimeframe`.
    """
    dirname = os.path.dirname(__file__)
    test_file = os.path.join(dirname, "test_h4.csv")
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.D1)
    incompatible_timeframe_raised = False

    try:
        run_backtest(strategy_t=stumb_strategy, 
                     data_provider_factory=candles, 
                     start_money=10_000, 
                     since=datetime.now(),
                     until=datetime.now(),
                     maker_fee=Decimal('0.000'), 
                     taker_fee=Decimal('0.000'))
    except IncompatibleTimeframe:
        incompatible_timeframe_raised = True
    assert incompatible_timeframe_raised
