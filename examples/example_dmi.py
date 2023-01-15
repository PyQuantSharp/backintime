from datetime import datetime
from backintime.backtester import Backtester
from backintime.trading_strategy import TradingStrategy
from backintime.timeframes import Timeframes as tf
from backintime.analyser.indicators.dmi import DMIFactory as dmi
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
    Example DMI strategy.

    Buy if +DI > -DI and ADX increases.
    Sell if +DI < -DI or ADX decreases.
    """
    title = "Example DMI strategy"
    indicators = { dmi(tf.H4) }

    def tick(self):
        dmi = self.analyser.dmi(tf.H4)
        if not self.position and dmi_buy_signal(dmi)
            self.buy()

        elif self.position and dmi_sell_signal(dmi)
            self.sell()


feed = BinanceCandlesFactory('BTCUSDT', tf.M1)
since = datetime.fromisoformat("2020-01-01 00:00+00:00")
until = datetime.fromisoformat("2021-01-01 00:00+00:00")

backtester = Backtester(DMIStrategy, feed)
result = backtester.run(10_000, since, until, 
                        maker_fee='0.005', taker_fee='0.005')
print(result)
print(result.get_stats('FIFO'))
result.export()