import typing as t
from datetime import datetime
from backintime import TradingStrategy, run_backtest
from backintime.timeframes import Timeframes as tf
from backintime.indicator_params import DMI
from backintime.analyser.indicators.dmi import DMIResultSequence
from backintime.data.binance import BinanceCandlesFactory


def dmi_buy_signal(dmi: DMIResultSequence) -> bool:
    """True, if +DI > -DI and ADX increases."""
    return dmi.positive_di[-1] > dmi.negative_di[-1] and dmi.adx_increases()


def dmi_sell_signal(dmi: DMIResultSequence) -> bool:
    """True, if +DI < -DI or ADX decreases."""
    return dmi.positive_di[-1] < dmi.negative_di[-1] or dmi.adx_decreases()


class DMIStrategy(TradingStrategy):
    """
    Sample DMI strategy.

    Buy if +DI > -DI and ADX increases.
    Sell if +DI < -DI or ADX decreases.
    """
    title = "Sample DMI strategy"
    indicators = { DMI(tf.H4) }

    def tick(self):
        dmi = self.analyser.dmi(tf.H4)
        if not self.position and dmi_buy_signal(dmi)
            self.buy()

        elif self.position and dmi_sell_signal(dmi)
            self.sell()


feed = BinanceCandlesFactory('BTCUSDT', tf.M1)
since = datetime.fromisoformat("2020-01-01 00:00+00:00")
until = datetime.fromisoformat("2021-01-01 00:00+00:00")

result = run_backtest(DMIStrategy, feed,
                      10_000, since, until, 
                      maker_fee='0.005', taker_fee='0.005')
print(result)
print(result.get_stats('FIFO'))
result.export()