import typing as t
from datetime import datetime
from backintime import TradingStrategy, run_backtest
from backintime.timeframes import Timeframes as tf
from backintime.indicator_params import ATR, RSI
from backintime.data.binance import BinanceCandlesFactory


class AtrRsiStrategy(TradingStrategy):
    title = "Sample ATR/RSI strategy"
    candle_timeframes = { tf.H4, tf.D1 }
    indicators = { 
        ATR(tf.H4), 
        RSI(tf.H4), 
        RSI(tf.D1) 
    }

    def __init__(self, broker, analyser, candles):
        self.last_buy: t.Optional[OrderInfo] = None
        super().__init__(broker, analyser, candles)

    def tick(self):
        if not self.position:
            rsi_d1 = self.analyser.rsi(tf.D1)[-1]
            if rsi_d1 > 50:
                current_candle = self.candles.get(tf.H4)
                price = current_candle.close
                atr_h4 = self.analyser.atr(tf.H4)[-1]
                if atr_h4 >= price*0.02:
                    self.last_buy = self.buy()

        elif self.position:
            rsi_h4 = self.analyser.rsi(tf.H4)[-1]
            atr_h4 = self.analyser.atr(tf.H4)[-1]
            price = self.last_buy.fill_price
            if rsi_h4 <= 50 or atr_h4 < price*0.02:
                self.sell()


feed = BinanceCandlesFactory('BTCUSDT', tf.M1)
since = datetime.fromisoformat("2020-01-01 00:00+00:00")
until = datetime.fromisoformat("2021-01-01 00:00+00:00")

result = run_backtest(AtrRsiStrategy, feed,
                      10_000, since, until, 
                      maker_fee='0.005', taker_fee='0.005')
print(result)
print(result.get_stats('FIFO'))
result.export()