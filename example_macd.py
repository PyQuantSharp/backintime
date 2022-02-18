from backtesting import (
    Backtester,
    BinanceApiCandles,
    TradingStrategy,
    Timeframes,
    CandleProperties
)
from backtesting.oscillators.macd import macd


class MacdStrategy(TradingStrategy):

    using_oscillators = ( macd(Timeframes.H4), )

    def __call__(self):
        macd = self.oscillators.get('MACD_H4')

        if not self.position and macd.crossover_up():
            self._buy()

        elif self.position and macd.crossover_down():
            self._sell()


feed = BinanceApiCandles('BTCUSDT', Timeframes.H4)
backtester = Backtester(MacdStrategy, feed)
backtester.run_test('2020-01-01', 10000)
print(backtester.results())
