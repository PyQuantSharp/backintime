from datetime import datetime
from backintime.v163.data import BinanceCandles
from backintime.v163.timeframes import Timeframes as tf


since = datetime.fromisoformat("2022-10-10")

candles = BinanceCandles("BTCUSDT", tf.H4, since)
for candle in candles:
	print(f"Candle: {candle}")