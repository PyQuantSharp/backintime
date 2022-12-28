import typing as t
from datetime import datetime
from decimal import Decimal
from backintime.data.data_provider import DataProviderError
from backintime.timeframes import Timeframes as tf
from backintime.data.csv import (
    CSVCandlesFactory, 
    Candle, 
    DateNotFound, 
    InconsistentData
)


def _candles_equal(first_candle: Candle, second_candle: Candle) -> bool:
    # TODO: consider implement it as a Candle method
    return (first_candle.open_time == second_candle.open_time and \
            first_candle.open == second_candle.open and \
            first_candle.high == second_candle.high and \
            first_candle.low == second_candle.low and \
            first_candle.close == second_candle.close and \
            first_candle.close_time == second_candle.close_time and \
            first_candle.volume == second_candle.volume)


def test_first_candle_open_time():
    """Ensure that the first candle has `open_time` >= `since` param."""
    test_file = 'test_h4_candles.csv'
    since = datetime.fromisoformat("2018-01-01 00:00+00:00")
    until = datetime.fromisoformat("2018-01-01 08:00+00:00")
    candles = CSVCandlesFactory(test_file, "BTCUSDT", tf.H4)
    candles = candles.create(since, until)

    first_candle = next(iter(candles))
    assert first_candle.open_time >= since


def test_last_candle_close_time():
    """Ensure that the last candle has `close_time` < `until` param."""
    test_file = 'test_h4_candles.csv'
    since = datetime.fromisoformat("2018-01-01 00:00+00:00")
    until = datetime.fromisoformat("2018-01-07 08:00+00:00")
    candles = CSVCandlesFactory(test_file, "BTCUSDT", tf.H4)
    candles = candles.create(since, until)
    last_candle: t.Optional[Candle] = None

    for candle in candles:
        last_candle = candle
    assert last_candle and last_candle.close_time < until


def test_candle_data_matches_expected():
    """
    Ensure that candle data matches expected. 
    Hardcoded candle data valid for 2018-01-07 00:00, H4 is used.
    """
    test_file = 'test_h4_candles.csv'
    since = datetime.fromisoformat("2018-01-07 00:00+00:00")
    until = datetime.fromisoformat("2018-01-07 04:00+00:00")
    candles = CSVCandlesFactory(test_file, "BTCUSDT", tf.H4)
    candles = candles.create(since, until)

    expected_close = '2018-01-07 03:59:59.999000+00:00'
    expected_close = datetime.fromisoformat(expected_close)
    expected_candle = Candle(open_time=since,
                             open=Decimal('17069.79'),
                             high=Decimal('17099.96'),
                             low=Decimal('16605.01'),
                             close=Decimal('16740.68'),
                             close_time=expected_close,
                             volume=Decimal('3154.30460300'))

    candle = next(iter(candles))
    assert _candles_equal(expected_candle, candle)


def test_not_found_date_will_raise():
    """
    Ensure that passing date not present in CSV file 
    will raise `DateNotFound`.
    """
    test_file = 'test_h4_candles.csv'
    since = datetime.fromisoformat("2023-01-01 00:00+00:00")
    until = datetime.fromisoformat("2024-01-01 00:00+00:00")
    candles = CSVCandlesFactory(test_file, "BTCUSDT", tf.H4)
    candles = candles.create(since, until)
    date_not_found_raised = False

    try:
        next(iter(candles))
    except DateNotFound:
        date_not_found_raised = True
    assert date_not_found_raised


def test_inconsistent_data_will_raise():
    """
    Ensure that iterating over CSV file with inconsistent data 
    (some candle has `open_time` < `close_time` of prev. candle) 
    will raise `InconsistentData`.
    """
    test_file = 'inconsistent_h4_candles.csv'
    since = datetime.fromisoformat("2018-01-01 00:00+00:00")
    until = datetime.fromisoformat("2018-01-07 00:00+00:00")
    candles = CSVCandlesFactory(test_file, "BTCUSDT", tf.H4)
    candles = candles.create(since, until)
    inconsistent_data_raised = False

    try:
        for candle in candles:
            pass
    except InconsistentData:
        inconsistent_data_raised = True
    assert inconsistent_data_raised
