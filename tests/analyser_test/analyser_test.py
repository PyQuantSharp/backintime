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