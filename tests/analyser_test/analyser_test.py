from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from backintime.data.csv import CSVCandlesFactory
from backintime.analyser.analyser import Analyser, AnalyserBuffer
from backintime.analyser.indicators.macd import MacdFactory
from backintime.analyser.indicators.sma import SMAFactory
from backintime.analyser.indicators.ema import EMAFactory
from backintime.analyser.indicators.atr import ATRFactory
from backintime.analyser.indicators.rsi import RSIFactory
from backintime.analyser.indicators.bbands import BbandsFactory
from backintime.analyser.indicators.dmi import DMIFactory
from backintime.analyser.indicators.adx import ADXFactory
from backintime.analyser.indicators.pivot import PivotPointsFactory
from backintime.analyser.indicators.pivot import CLASSIC_PIVOT
from backintime.analyser.indicators.pivot import TRADITIONAL_PIVOT
from backintime.analyser.indicators.pivot import FIBONACCI_PIVOT
from backintime.analyser.indicators.constants import HIGH, LOW, CLOSE
from backintime.timeframes import Timeframes as tf
from backintime.timeframes import estimate_open_time


def test_macd():
    """
    Ensure that calculated macd values match expected 
    with at least 2 floating points precision,
    using valid MACD for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    macd = MacdFactory(tf.H4)
    quantity = macd.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { macd })

    expected_macd = Decimal('151.30')
    expected_signal = Decimal('66.56')
    expected_hist = Decimal('84.74')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    macd = analyser.get_last('macd_h4')

    macd_diff = (Decimal(macd.macd) - expected_macd).copy_abs()
    macd_diff = macd_diff.quantize(expected_precision, ROUND_HALF_UP)

    signal_diff = (Decimal(macd.signal) - expected_signal).copy_abs()
    signal_diff = signal_diff.quantize(expected_precision, ROUND_HALF_UP)

    hist_diff = (Decimal(macd.hist) - expected_hist).copy_abs()
    hist_diff = hist_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert macd_diff <= expected_precision
    assert signal_diff <= expected_precision
    assert hist_diff <= expected_precision


def test_macd_len():
    """
    Ensure that MACD calculation results in a sequence 
    with expected length.
    """
    macd = MacdFactory(tf.H4)
    quantity = macd.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { macd })

    for candle in candles:
        analyser_buffer.update(candle)

    macd = analyser.get('macd_h4')
    assert len(macd) == expected_len


def test_sma():
    """
    Ensure that calculated SMA with period of 9 
    matches expected with at least 2 floating points precision,
    using valid SMA for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    sma = SMAFactory(tf.H4, CLOSE, 9)
    quantity = sma.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { sma })

    expected_sma = Decimal('16773.72')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    sma = analyser.get_last('sma_h4')
    sma_diff = (Decimal(sma) - expected_sma).copy_abs()
    sma_diff = sma_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert sma_diff <= expected_precision


def test_sma_len():
    """
    Ensure that SMA calculation results in a sequence 
    with expected length.
    """
    sma = SMAFactory(tf.H4, CLOSE, 9)
    quantity = sma.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { sma })

    for candle in candles:
        analyser_buffer.update(candle)

    sma = analyser.get('sma_h4')
    assert len(sma) == expected_len


def test_ema_9():
    """
    Ensure that calculated EMA with period of 9 
    matches expected with at least 2 floating points precision,
    using valid EMA for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    ema = EMAFactory(tf.H4, CLOSE, 9)
    quantity = ema.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { ema })

    expected_ema = Decimal('16833.64')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    ema = analyser.get_last('ema_h4')
    ema_diff = (Decimal(ema) - expected_ema).copy_abs()
    ema_diff = ema_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert ema_diff <= expected_precision


def test_ema_9_len():
    """
    Ensure that EMA calculation with period of 9 
    results in a sequence with expected length.
    """
    ema = EMAFactory(tf.H4, CLOSE, 9)
    quantity = ema.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { ema })

    for candle in candles:
        analyser_buffer.update(candle)

    ema = analyser.get('ema_h4')
    assert len(ema) == expected_len


def test_ema_100():
    """
    Ensure that calculated EMA with period of 100 
    matches expected with at least 2 floating points precision,
    using valid EMA for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    ema = EMAFactory(tf.H4, CLOSE, 100)
    quantity = ema.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { ema })

    expected_ema = Decimal('16814.00')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    ema = analyser.get_last('ema_h4')
    ema_diff = (Decimal(ema) - expected_ema).copy_abs()
    ema_diff = ema_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert ema_diff <= expected_precision


def test_atr():
    """
    Ensure that calculated ATR with period of 14 
    matches expected with at least 2 floating points precision,
    using valid ATR for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    atr = ATRFactory(tf.H4)
    quantity = atr.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, HIGH, quantity)
    analyser_buffer.reserve(tf.H4, LOW, quantity)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { atr })

    expected_atr = Decimal('211.47')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    atr = analyser.get_last('atr_h4')
    atr_diff = (Decimal(atr) - expected_atr).copy_abs()
    atr_diff = atr_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert atr_diff <= expected_precision


def test_atr_len():
    """
    Ensure that ATR calculation results in a sequence 
    with expected length.
    """
    atr = ATRFactory(tf.H4)
    quantity = atr.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, HIGH, quantity)
    analyser_buffer.reserve(tf.H4, LOW, quantity)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { atr })

    for candle in candles:
        analyser_buffer.update(candle)

    atr = analyser.get('atr_h4')
    assert len(atr) == expected_len


def test_rsi():
    """
    Ensure that calculated RSI with period of 14 
    matches expected with at least 2 floating points precision,
    using valid RSI for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    rsi = RSIFactory(tf.H4)
    quantity = rsi.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { rsi })

    expected_rsi = Decimal('75.35')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    rsi = analyser.get_last('rsi_h4')
    rsi_diff = (Decimal(rsi) - expected_rsi).copy_abs()
    rsi_diff = rsi_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert rsi_diff <= expected_precision


def test_rsi_len():
    """
    Ensure that RSI calculation results in a sequence 
    with expected length.
    """
    rsi = RSIFactory(tf.H4)
    quantity = rsi.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { rsi })

    for candle in candles:
        analyser_buffer.update(candle)

    rsi = analyser.get('rsi_h4')
    assert len(rsi) == expected_len


def test_bbands():
    """
    Ensure that calculated BBANDS values match expected 
    with at least 2 floating points precision,
    using valid BBANDS for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    bbands = BbandsFactory(tf.H4)
    quantity = bbands.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { bbands })

    expected_middle_band = Decimal('16519.69')
    expected_upper_band = Decimal('17138.52')
    expected_lower_band = Decimal('15900.85')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    bbands = analyser.get_last('bbands_h4')

    upper_band = bbands.upper_band
    upper_band_diff = (Decimal(upper_band) - expected_upper_band).copy_abs()
    upper_band_diff = upper_band_diff.quantize(expected_precision, ROUND_HALF_UP)

    mid_band = bbands.middle_band
    mid_band_diff = (Decimal(mid_band) - expected_middle_band).copy_abs()
    mid_band_diff = mid_band_diff.quantize(expected_precision, ROUND_HALF_UP)

    lower_band = bbands.lower_band
    lower_band_diff = (Decimal(lower_band) - expected_lower_band).copy_abs()
    lower_band_diff = lower_band_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert upper_band_diff <= expected_precision
    assert mid_band_diff <= expected_precision
    assert lower_band_diff <= expected_precision


def test_bbands_len():
    """
    Ensure that BBANDS calculation results in a sequence 
    with expected length.
    """
    bbands = BbandsFactory(tf.H4)
    quantity = bbands.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { bbands })

    for candle in candles:
        analyser_buffer.update(candle)

    bbands = analyser.get('bbands_h4')
    assert len(bbands) == expected_len


def test_dmi():
    """
    Ensure that calculated DMI values match expected 
    with at least 2 floating points precision,
    using valid DMI for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    dmi = DMIFactory(tf.H4)
    quantity = dmi.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, HIGH, quantity)
    analyser_buffer.reserve(tf.H4, LOW, quantity)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { dmi })

    expected_adx = Decimal('27.1603')
    expected_positive_di = Decimal('34.2968')
    expected_negative_di = Decimal('14.7384')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    dmi = analyser.get_last("dmi_h4")

    positive_di = dmi.positive_di
    pos_di_diff = (Decimal(positive_di) - expected_positive_di).copy_abs()
    pos_di_diff = pos_di_diff.quantize(expected_precision, ROUND_HALF_UP)

    negative_di = dmi.negative_di
    neg_di_diff = (Decimal(negative_di) - expected_negative_di).copy_abs()
    neg_di_diff = neg_di_diff.quantize(expected_precision, ROUND_HALF_UP)

    adx = dmi.adx
    adx_diff = (Decimal(adx) - expected_adx).copy_abs()
    adx_diff = adx_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert adx_diff <= expected_precision
    assert pos_di_diff <= expected_precision
    assert neg_di_diff <= expected_precision


def test_dmi_len():
    """
    Ensure that DMI calculation results in a sequence 
    with expected length.
    """
    dmi = DMIFactory(tf.H4)
    quantity = dmi.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, HIGH, quantity)
    analyser_buffer.reserve(tf.H4, LOW, quantity)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { dmi })

    for candle in candles:
        analyser_buffer.update(candle)

    dmi = analyser.get("dmi_h4")
    assert len(dmi) == expected_len


def test_adx():
    """
    Ensure that calculated ADX value match expected 
    with at least 2 floating points precision,
    using valid ADX for 2022-30-11 23:59 UTC, H4 (Binance) 
    as a reference value.
    """
    adx = ADXFactory(tf.H4)
    quantity = adx.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, HIGH, quantity)
    analyser_buffer.reserve(tf.H4, LOW, quantity)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { adx })

    expected_adx = Decimal('27.1603')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    adx = analyser.get_last("adx_h4")
    adx_diff = (Decimal(adx) - expected_adx).copy_abs()
    adx_diff = adx_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert adx_diff <= expected_precision


def test_adx_len():
    """
    Ensure that ADX calculation results in a sequence 
    with expected length.
    """
    adx = ADXFactory(tf.H4)
    quantity = adx.indicator_params[0].quantity
    expected_len = quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.H4, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.H4, HIGH, quantity)
    analyser_buffer.reserve(tf.H4, LOW, quantity)
    analyser_buffer.reserve(tf.H4, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { adx })

    for candle in candles:
        analyser_buffer.update(candle)

    adx = analyser.get("adx_h4")
    assert len(adx) == expected_len


def test_classic_pivot():
    """
    Ensure that calculated PIVOT values (classic) with daily period
    match expected with at least 2 floating points precision,
    using valid PIVOT for 2022-30-11 23:59 UTC, H4 (Binance) 
    as reference values.
    """
    pivot = PivotPointsFactory(tf.D1, pivot_type=CLASSIC_PIVOT)
    quantity = pivot.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.D1, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.D1, HIGH, quantity)
    analyser_buffer.reserve(tf.D1, LOW, quantity)
    analyser_buffer.reserve(tf.D1, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { pivot })

    expected_pivot = Decimal('16363.75')
    expected_s1 = Decimal('16178.78')
    expected_s2 = Decimal('15915.04')
    expected_s3 = Decimal('15466.33')
    expected_s4 = Decimal('15017.62')
    expected_r1 = Decimal('16627.49')
    expected_r2 = Decimal('16812.46')
    expected_r3 = Decimal('17261.17')
    expected_r4 = Decimal('17709.88')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    pivot = analyser.get_last("pivot_d1")
    pivot_diff = (Decimal(pivot.pivot) - expected_pivot).copy_abs()
    pivot_diff = pivot_diff.quantize(expected_precision, ROUND_HALF_UP)

    s1_diff = (Decimal(pivot.s1) - expected_s1).copy_abs()
    s1_diff = s1_diff.quantize(expected_precision, ROUND_HALF_UP)

    s2_diff = (Decimal(pivot.s2) - expected_s2).copy_abs()
    s2_diff = s2_diff.quantize(expected_precision, ROUND_HALF_UP)

    s3_diff = (Decimal(pivot.s3) - expected_s3).copy_abs()
    s3_diff = s3_diff.quantize(expected_precision, ROUND_HALF_UP)

    s4_diff = (Decimal(pivot.s4) - expected_s4).copy_abs()
    s4_diff = s4_diff.quantize(expected_precision, ROUND_HALF_UP)

    r1_diff = (Decimal(pivot.r1) - expected_r1).copy_abs()
    r1_diff = r1_diff.quantize(expected_precision, ROUND_HALF_UP)

    r2_diff = (Decimal(pivot.r2) - expected_r2).copy_abs()
    r2_diff = r2_diff.quantize(expected_precision, ROUND_HALF_UP)

    r3_diff = (Decimal(pivot.r3) - expected_r3).copy_abs()
    r3_diff = r3_diff.quantize(expected_precision, ROUND_HALF_UP)

    r4_diff = (Decimal(pivot.r4) - expected_r4).copy_abs()
    r4_diff = r4_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert pivot_diff <= expected_precision
    assert s1_diff <= expected_precision
    assert s2_diff <= expected_precision
    assert s3_diff <= expected_precision
    assert s4_diff <= expected_precision
    assert r1_diff <= expected_precision
    assert r2_diff <= expected_precision
    assert r3_diff <= expected_precision
    assert r4_diff <= expected_precision


def test_classic_pivot_len():
    """
    Ensure that PIVOT (classic) calculation results 
    in a sequence with expected length.
    """
    pivot = PivotPointsFactory(tf.D1, pivot_type=CLASSIC_PIVOT)
    quantity = pivot.indicator_params[0].quantity
    expected_len = quantity - 1

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.D1, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.D1, HIGH, quantity)
    analyser_buffer.reserve(tf.D1, LOW, quantity)
    analyser_buffer.reserve(tf.D1, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { pivot })

    for candle in candles:
        analyser_buffer.update(candle)

    pivot = analyser.get("pivot_d1")
    assert len(pivot) == expected_len


def test_traditional_pivot():
    """
    Ensure that calculated PIVOT values (traditional) with daily period
    match expected with at least 2 floating points precision,
    using valid PIVOT for 2022-30-11 23:59 UTC, H4 (Binance) 
    as reference values.
    """
    pivot = PivotPointsFactory(tf.D1, pivot_type=TRADITIONAL_PIVOT)
    quantity = pivot.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.D1, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.D1, HIGH, quantity)
    analyser_buffer.reserve(tf.D1, LOW, quantity)
    analyser_buffer.reserve(tf.D1, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { pivot })

    expected_pivot = Decimal('16363.75')
    expected_s1 = Decimal('16178.78')
    expected_s2 = Decimal('15915.04')
    expected_s3 = Decimal('15730.07')
    expected_s4 = Decimal('15545.11')
    expected_s5 = Decimal('15360.15')
    expected_r1 = Decimal('16627.49')
    expected_r2 = Decimal('16812.46')
    expected_r3 = Decimal('17076.20')
    expected_r4 = Decimal('17339.95')
    expected_r5 = Decimal('17603.70')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    pivot = analyser.get_last("pivot_d1")
    pivot_diff = (Decimal(pivot.pivot) - expected_pivot).copy_abs()
    pivot_diff = pivot_diff.quantize(expected_precision, ROUND_HALF_UP)

    s1_diff = (Decimal(pivot.s1) - expected_s1).copy_abs()
    s1_diff = s1_diff.quantize(expected_precision, ROUND_HALF_UP)

    s2_diff = (Decimal(pivot.s2) - expected_s2).copy_abs()
    s2_diff = s2_diff.quantize(expected_precision, ROUND_HALF_UP)

    s3_diff = (Decimal(pivot.s3) - expected_s3).copy_abs()
    s3_diff = s3_diff.quantize(expected_precision, ROUND_HALF_UP)

    s4_diff = (Decimal(pivot.s4) - expected_s4).copy_abs()
    s4_diff = s4_diff.quantize(expected_precision, ROUND_HALF_UP)

    s5_diff = (Decimal(pivot.s5) - expected_s5).copy_abs()
    s5_diff = s5_diff.quantize(expected_precision, ROUND_HALF_UP)

    r1_diff = (Decimal(pivot.r1) - expected_r1).copy_abs()
    r1_diff = r1_diff.quantize(expected_precision, ROUND_HALF_UP)

    r2_diff = (Decimal(pivot.r2) - expected_r2).copy_abs()
    r2_diff = r2_diff.quantize(expected_precision, ROUND_HALF_UP)

    r3_diff = (Decimal(pivot.r3) - expected_r3).copy_abs()
    r3_diff = r3_diff.quantize(expected_precision, ROUND_HALF_UP)

    r4_diff = (Decimal(pivot.r4) - expected_r4).copy_abs()
    r4_diff = r4_diff.quantize(expected_precision, ROUND_HALF_UP)

    r5_diff = (Decimal(pivot.r5) - expected_r5).copy_abs()
    r5_diff = r5_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert pivot_diff <= expected_precision
    assert s1_diff <= expected_precision
    assert s2_diff <= expected_precision
    assert s3_diff <= expected_precision
    assert s4_diff <= expected_precision
    assert s5_diff <= expected_precision
    assert r1_diff <= expected_precision
    assert r2_diff <= expected_precision
    assert r3_diff <= expected_precision
    assert r4_diff <= expected_precision
    assert r5_diff <= expected_precision


def test_traditional_pivot_len():
    """
    Ensure that PIVOT (traditional) calculation results 
    in a sequence with expected length.
    """
    pivot = PivotPointsFactory(tf.D1, pivot_type=TRADITIONAL_PIVOT)
    quantity = pivot.indicator_params[0].quantity
    expected_len = quantity - 1

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.D1, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.D1, HIGH, quantity)
    analyser_buffer.reserve(tf.D1, LOW, quantity)
    analyser_buffer.reserve(tf.D1, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { pivot })

    for candle in candles:
        analyser_buffer.update(candle)

    pivot = analyser.get("pivot_d1")
    assert len(pivot) == expected_len


def test_fibonacci_pivot():
    """
    Ensure that calculated PIVOT values (fibonacci) with daily period
    match expected with at least 2 floating points precision,
    using valid PIVOT for 2022-30-11 23:59 UTC, H4 (Binance) 
    as reference values.
    """
    pivot = PivotPointsFactory(tf.D1, pivot_type=FIBONACCI_PIVOT)
    quantity = pivot.indicator_params[0].quantity

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.D1, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.D1, HIGH, quantity)
    analyser_buffer.reserve(tf.D1, LOW, quantity)
    analyser_buffer.reserve(tf.D1, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { pivot })

    expected_pivot = Decimal('16363.75')
    expected_s1 = Decimal('16192.34')
    expected_s2 = Decimal('16086.44')
    expected_s3 = Decimal('15915.04')
    expected_r1 = Decimal('16535.15')
    expected_r2 = Decimal('16641.05')
    expected_r3 = Decimal('16812.46')
    expected_precision = Decimal('0.01')

    for candle in candles:
        analyser_buffer.update(candle)

    pivot = analyser.get_last("pivot_d1")
    pivot_diff = (Decimal(pivot.pivot) - expected_pivot).copy_abs()
    pivot_diff = pivot_diff.quantize(expected_precision, ROUND_HALF_UP)

    s1_diff = (Decimal(pivot.s1) - expected_s1).copy_abs()
    s1_diff = s1_diff.quantize(expected_precision, ROUND_HALF_UP)

    s2_diff = (Decimal(pivot.s2) - expected_s2).copy_abs()
    s2_diff = s2_diff.quantize(expected_precision, ROUND_HALF_UP)

    s3_diff = (Decimal(pivot.s3) - expected_s3).copy_abs()
    s3_diff = s3_diff.quantize(expected_precision, ROUND_HALF_UP)

    r1_diff = (Decimal(pivot.r1) - expected_r1).copy_abs()
    r1_diff = r1_diff.quantize(expected_precision, ROUND_HALF_UP)

    r2_diff = (Decimal(pivot.r2) - expected_r2).copy_abs()
    r2_diff = r2_diff.quantize(expected_precision, ROUND_HALF_UP)

    r3_diff = (Decimal(pivot.r3) - expected_r3).copy_abs()
    r3_diff = r3_diff.quantize(expected_precision, ROUND_HALF_UP)

    assert pivot_diff <= expected_precision
    assert s1_diff <= expected_precision
    assert s2_diff <= expected_precision
    assert s3_diff <= expected_precision
    assert r1_diff <= expected_precision
    assert r2_diff <= expected_precision
    assert r3_diff <= expected_precision


def test_fibonacci_pivot_len():
    """
    Ensure that PIVOT (fibonacci) calculation results 
    in a sequence with expected length.
    """
    pivot = PivotPointsFactory(tf.D1, pivot_type=FIBONACCI_PIVOT)
    quantity = pivot.indicator_params[0].quantity
    expected_len = quantity - 1

    test_file = 'test_h4.csv'
    until = datetime.fromisoformat('2022-12-01 00:00+00:00')
    since = estimate_open_time(until, tf.D1, -quantity)
    candles = CSVCandlesFactory(test_file, 'BTCUSDT', tf.H4)
    candles = candles.create(since, until)

    analyser_buffer = AnalyserBuffer(since)
    analyser_buffer.reserve(tf.D1, HIGH, quantity)
    analyser_buffer.reserve(tf.D1, LOW, quantity)
    analyser_buffer.reserve(tf.D1, CLOSE, quantity)
    analyser = Analyser(analyser_buffer, { pivot })

    for candle in candles:
        analyser_buffer.update(candle)

    pivot = analyser.get("pivot_d1")
    assert len(pivot) == expected_len