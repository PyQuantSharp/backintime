import numpy
import typing as t
from datetime import datetime
from decimal import Decimal
from backintime import TradingStrategy, run_backtest
from backintime.timeframes import Timeframes as tf
from backintime.data.binance import BinanceCandlesFactory
from backintime.indicator_params import SMA, MACD, DMI, PIVOT
from backintime.analyser.indicators.dmi import DMIResultSequence
from backintime.analyser.indicators.macd import MacdResultSequence
from backintime.broker import TakeProfitOptions, StopLossOptions


def macd_hist_up(macd: MacdResultSequence) -> bool:
    """True, if MACD hist > 0."""
    return macd[-1].hist > 0


def dmi_buy_signal(dmi: DMIResultSequence) -> bool:
    """True, if +DI > -DI."""
    return dmi.positive_di[-1] > dmi.negative_di[-1]


class SmaResistanceBreakout(TradingStrategy):
    title = "SMA resistance breakout"
    candle_timeframes = { tf.M15 }
    indicators = {
        SMA(tf.M15, 55),
        MACD(tf.M15),
        DMI(tf.M15, 14),
        PIVOT(tf.D1, 15)
    }

    def __init__(self, broker, analyser, candles):
        self.prev_close: t.Optional[Decimal] = None
        self.curr_close: t.Optional[Decimal] = None
        super().__init__(broker, analyser, candles)

    def tick(self):
        self.prev_close = self.curr_close
        self.curr_close = self.candles.get(tf.M15).close
        sma = self.analyser.sma(tf.M15, period=55)[-1]
        sma_crossover_up = self.curr_close > sma and \
                           self.prev_close and self.prev_close <= sma

        if self.broker.max_fiat_for_maker and sma_crossover_up and \
                macd_hist_up(self.analyser.macd(tf.M15)) and \
                dmi_buy_signal(self.analyser.dmi(tf.M15, 14)):
            # Calculate buy price: current SMA + 0.2%
            limit_price = Decimal(sma) * Decimal('1.002')
            # Set up TP at PIVOT' R2 level
            pivot = self.analyser.pivot(tf.D1, 15)
            take_profit_trigger = pivot[-1].r2
            take_profit = TakeProfitOptions(percentage_amount=Decimal('100.00'),
                                            trigger_price=take_profit_trigger)
            # Set up SL at current close price - 5%
            stop_loss_trigger = self.candles.get(tf.M15).close * Decimal('0.95')
            stop_loss = StopLossOptions(percentage_amount=Decimal('100.00'), 
                                        trigger_price=stop_loss_trigger)
            # Submit limit buy with TP & SL
            self.limit_buy(order_price=limit_price,
                           amount=self.broker.max_fiat_for_maker,
                           take_profit=take_profit,
                           stop_loss=stop_loss)


feed = BinanceCandlesFactory('BTCUSDT', tf.M15)
since = datetime.fromisoformat("2020-03-01 00:00+00:00")
until = datetime.fromisoformat("2021-05-01 00:00+00:00")

result = run_backtest(SmaResistanceBreakout, feed, 
                      10_000, since, until, 
                      maker_fee='0.005', taker_fee='0.005')

print(result)
print(result.get_stats('FIFO'))
print(result.get_stats('LIFO'))
print(result.get_stats('AVCO'))
result.export()
