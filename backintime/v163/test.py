from datetime import datetime
from backintime.v163.trading_strategy import TradingStrategy
from backintime.v163.data.binance import BinanceCandles
from backintime.v163.timeframes import Timeframes as tf
from backintime.v163.backtester import Backtester


class MyStrategy(TradingStrategy):
	def tick(self):
		pass


since = datetime.fromisoformat("2022-10-10")

candles = BinanceCandles("BTCUSDT", tf.H4, since)
backtester = Backtester(MyStrategy, candles)
backtester.run(None, None)