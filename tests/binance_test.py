import typing as t
from datetime import datetime
from decimal import Decimal
from backintime.data.binance import BinanceCandles, Candle
from backintime.timeframes import Timeframes as tf


def _candles_equal(first_candle: Candle, second_candle: Candle) -> bool:
    # TODO: consider implement it as a Candle method
    return (first_candle.open_time == second_candle.open_time and \
            first_candle.open == second_candle.open and \
            first_candle.high == second_candle.high and \
            first_candle.low == second_candle.low and \
            first_candle.close == second_candle.close and \
            first_candle.close_time == second_candle.close_time and \
            first_candle.volume == second_candle.volume)


def test_binance_candles_order():
    """Check whether yield binance candles in consistent order."""
    since = datetime.fromisoformat("2018-01-01 00:00+00:00")
    until = datetime.fromisoformat("2019-01-01 08:00+00:00")
    candles = BinanceCandles("BTCUSDT", tf.H4, since, until)
    prev_open: t.Optional[datetime] = None

    for candle in candles:
        if prev_open:
            assert candle.open_time >= prev_open, f"{candle.open_time} follows {prev_open}"
        prev_open = candle.open_time
    assert prev_open is not None


def test_binance_candles_has_missing():
    """There were several missing candles in 2018-2019."""
    since = datetime.fromisoformat("2018-01-01 00:00+00:00")
    until = datetime.fromisoformat("2019-01-01 08:00+00:00")
    candles = BinanceCandles("BTCUSDT", tf.H4, since, until)
    prev_open: t.Optional[datetime] = None
    has_missing = False

    for candle in candles:
        if prev_open:
            delta = candle.open_time - prev_open
            delta = delta.total_seconds()
            if delta > tf.H4.value:
                print(f"NOTE: Missing candle after: {prev_open}. "
                      f"Next open: {candle.open_time}")
                has_missing = True
        prev_open = candle.open_time
    assert has_missing


def test_first_candle_open_time():
    """Ensure that the first candle has `open_time` >= `since` param."""
    since = datetime.fromisoformat("2018-01-01 00:00+00:00")
    until = datetime.fromisoformat("2018-01-01 08:00+00:00")
    candles = BinanceCandles("BTCUSDT", tf.H4, since, until)
    first_candle = next(iter(candles))
    assert first_candle.open_time >= since


def test_last_candle_close_time():
    """Ensure that the last candle has `close_time` < `until` param."""
    since = datetime.fromisoformat("2018-01-01 00:00+00:00")
    until = datetime.fromisoformat("2018-01-07 08:00+00:00")
    candles = BinanceCandles("BTCUSDT", tf.H4, since, until)
    last_candle: t.Optional[Candle] = None

    for candle in candles:
        last_candle = candle
    assert last_candle and last_candle.close_time < until


def test_candle_data_matches_expected():
    """
    Ensure that candle data matches expected. 
    Hardcoded candle data valid for 2022-12-01 00:00, H1 is used.
    """
    since = datetime.fromisoformat("2022-12-01 00:00+00:00")
    until = datetime.fromisoformat("2022-12-01 01:00+00:00")
    candles = BinanceCandles("BTCUSDT", tf.H1, since, until)
    
    expected_close = '2022-12-01 00:59:59.999000+00:00'
    expected_close = datetime.fromisoformat(expected_close)
    expected_candle = Candle(open_time=since,
                             open=Decimal('17165.53'),
                             high=Decimal('17236.29'),
                             low=Decimal('17122.65'),
                             close=Decimal('17161.55'),
                             close_time=expected_close,
                             volume=Decimal('14452.68614'))

    candle = next(iter(candles))
    assert _candles_equal(expected_candle, candle)
