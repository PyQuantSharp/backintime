from backintime import (
    Backtester,
    BinanceApiCandles,
    TradingStrategy,
    Timeframes,
    CandleProperties
)
from backintime.oscillators.atr import atr
from backintime.oscillators.rsi import rsi


class MyStrategy(TradingStrategy):

    using_candles = (Timeframes.H4, Timeframes.D1)
    using_oscillators = (
        atr(Timeframes.H4, 14, 'ATR_H4', False),
        rsi(Timeframes.H4, 14, 'RSI_H4', False),
        rsi(Timeframes.D1, 14, 'RSI_D1', False)
    )

    def __call__(self):

        if not self.position:
            rsi_d1 = self.oscillators.get('RSI_D1')
            if rsi_d1 > 50:
                current_candle = self.candles.get(Timeframes.H4)
                price = current_candle.close
                atr_h4 = self.oscillators.get('ATR_H4')
                if atr_h4 >= price*0.02:
                    self._buy()

        elif self.position:
            rsi_h4 = self.oscillators.get('RSI_H4')
            atr_h4 = self.oscillators.get('ATR_H4')
            price = self.position.opening_price()
            if rsi_h4 <= 50 or atr_h4 < price*0.02:
                self._sell()


feed = BinanceApiCandles('BTCUSDT', Timeframes.H4)
backtester = Backtester(MyStrategy, feed)
backtester.run_test('2020-01-01', 10000)
print(backtester.results())
