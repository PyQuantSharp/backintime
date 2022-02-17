from backtesting import (
    Backtester,
    TradingStrategy,
    MarketDataAnalyzer,
    Timeframes,
    CandleProperties
)

from backtesting.candles_providers.timeframe_dump import TimeframeDump
from backtesting.candles_providers.timeframe_dump import TimeframeDumpScheme
from backtesting.oscillators.macd import MACD


class MacdAnalyzer(MarketDataAnalyzer):
    def __init__(self, market_data):
        oscillators = ( MACD(Timeframes.H4), )
        super().__init__(market_data, oscillators)


class MacdStrategy(TradingStrategy):

    analyzer_t = MacdAnalyzer

    def __call__(self):
        macd = self._oscillators.get('MACD_H4')

        if not self.position and macd.crossover_up():
            self._buy()

        elif self.position and macd.crossover_down():
            self._sell()


columns = TimeframeDumpScheme(
    open_time=0, close_time=6,
    open=1, high=3, low=4,
    close=2, volume=5
)
feed = TimeframeDump('h4.csv', Timeframes.H4, columns)
backtester = Backtester(MacdStrategy, feed)
backtester.run_test('2020-01-01', 10000)
print(backtester.results())
