from datetime import datetime
from backintime.trading_strategy import TradingStrategy
from backintime.timeframes import Timeframes as tf
from backintime.analyser.oscillators.macd import macd
from backintime.data.binance import BinanceCandlesFactory
from backintime.backtester import Backtester


class MacdStrategy(TradingStrategy):
    title = "Example MACD Strategy v0"
    oscillators = { macd(tf.H1) }

    def tick(self):
        macd = self.analyser.get('macd_h1')
        if not self.position and macd.crossover_up():
            self.buy()
        elif self.position and macd.crossover_down():
            self.sell()


feed = BinanceCandlesFactory('BTCUSDT', tf.M1)
since = datetime.fromisoformat("2020-01-01 00:00+00:00")
until = datetime.fromisoformat("2021-01-01 00:00+00:00")

backtester = Backtester(MacdStrategy, feed)
result = backtester.run(10_000, since, until, 
                        maker_fee='0.005', taker_fee='0.005')
print(result)
print(result.get_stats('FIFO'))
result.export()