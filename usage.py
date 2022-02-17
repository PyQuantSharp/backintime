from backtesting import (
    Backtester,
    TradingStrategy,
    MarketDataAnalyzer,
    Timeframes,
    CandleProperties
)

from backtesting.candles_providers.timeframe_dump import TimeframeDump
from backtesting.candles_providers.timeframe_dump import TimeframeDumpScheme
from backtesting.oscillators.atr import ATR
from backtesting.oscillators.rsi import RSI


class AtrRsiAnalyzer(MarketDataAnalyzer):
    def __init__(self, market_data):
        oscillators = (
            ATR(Timeframes.H4, 14, 'ATR_H4'),
            RSI(Timeframes.H4, 14, 'RSI_H4'),
            RSI(Timeframes.D1, 14, 'RSI_D1')
        )
        super().__init__(market_data, oscillators)


class MyStrategy(TradingStrategy):

    analyzer_t = AtrRsiAnalyzer
    using_candles = (Timeframes.H4, Timeframes.D1)

    def __call__(self):

        if not self.position:
            rsi_d1 = self._oscillators.get('RSI_D1')
            if rsi_d1 > 50:
                current_candle = self._timeframes_candle.get(Timeframes.H4)
                price = current_candle.close
                atr_h4 = self._oscillators.get('ATR_H4')
                if atr_h4 >= price*0.02:
                    self._buy()

        elif self.position:
            rsi_h4 = self._oscillators.get('RSI_H4')
            atr_h4 = self._oscillators.get('ATR_H4')
            price = self.position.opening_price()
            if rsi_h4 <= 50 or atr_h4 < price*0.02:
                self._sell()

# specify column indexes
columns = TimeframeDumpScheme(
    open_time=0, close_time=6,
    open=1, high=3, low=4,
    close=2, volume=5
)
feed = TimeframeDump('h4.csv', Timeframes.H4, columns)
# Backtester will test ts with feed, obviously
backtester = Backtester(MyStrategy, feed)
# choose start date and money for the test...
backtester.run_test('2020-01-01', 10000)
# (the last) result is a printable instance
result = backtester.results()
print(result)
# and also could be stored in a csv file
# result.to_csv('res.csv', sep=';')
