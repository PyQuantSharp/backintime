import typing as t

from datetime import datetime
from backintime.v163.trading_strategy import TradingStrategy
from backintime.v163.data.data_provider import DataProvider
from backintime.v163.exchange import Exchange
from backintime.v163.analyser import Analyser, AnalyserBuffer
from backintime.v163.candles import Candles, CandlesBuffer


class Backtester:
	def __init__(self, 
				 strategy_t: t.Type[TradingStrategy], 
				 market_data: DataProvider):
		self._strategy_t = strategy_t
		self._market_data = market_data

	def run(self, since: datetime, until: datetime):
		analyser_buffer = AnalyserBuffer()
		candles_buffer = CandlesBuffer(self._strategy_t.timeframes)
		exchange = Exchange(self._market_data)
		analyser = Analyser(self._strategy_t.oscillators, analyser_buffer)
		candles = Candles(candles_buffer)
		strategy = self._strategy_t(exchange, analyser, candles)
		ticks = 0

		for candle in exchange.candles():
			analyser_buffer.update(candle, ticks)
			candles_buffer.update(candle, ticks)
			strategy.tick()
            ticks += 1

		return exchange.get_trades() # wrap to instance with output methods
