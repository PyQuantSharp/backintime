# backtesting
✨ A framework for backtesting trading strategies with Python ✨

## Features
- Market/Limit orders management
- Support for 16 timeframes. Smaller can be used to imitate bigger.
- Quick trades statistics (winrate, avg profit, etc.)
- Export trades history to csv

## This is how it looks like - MACD strategy
[macd strategy desc link]
```py
from backtesting import TradingStrategy, Timeframes
from backtesting.oscillators.macd import MACD
'''
Extend TradingStrategy class and implement __call__ method
to have your own strategy
'''
class MacdStrategy(TradingStrategy):
    # declare required oscillators here for later use
    oscillators = ( MACD(Timeframes.H4), )

    def __call__(self):
        # runs each time a new candle closes
        macd = self._oscillators.get('MACD_H4')
        if not self.position and macd.crossover_up():
            self._buy()     # MarketBuy
        elif self.position and macd.crossover_down():
            self._sell()    # MarketSell
```
backtesting is done as follows:
(with binance API data)
```py
# add the following import to the ones above
from backtesting import BinanceApiCandles

feed = BinanceApiCandles('BTCUSDT', Timeframes.H4)
backtester = Backtester(MyStrategy, feed)
# choose start date and initial funds for the test
backtester.run_test('2020-01-01', 10000)
# the result is available as a printable instance
res = backtester.results()
print(res)
# and also can be saved to a csv file
res.to_csv('filename.csv', sep=';', summary=True)
```
Alternatively, you can use csv file on your local machine as source
```py
from backtesting import TimeframeDump, TimeframeDumpScheme
# specify column indexes in input csv
columns = TimeframeDumpScheme(
    open_time=0, close_time=6,
    open=1, high=3, low=4,
    close=2, volume=5)

feed = TimeframeDump('h4.csv', Timeframes.H4, columns)
backtester = Backtester(MyStrategy, feed)
backtester.run_test('2020-01-01', 10000)
print(backtester.results())
```

## Disclaimer
The project is currenctly in beta and misses few important features for <some-epitet>
usage. As of version 0.7.0 **NOT** yet developed:
- Trailing stop, Stop Loss and OCO mechanisms. Only Limit and Market orders supported
- Most oscillators. Ready-to-use oscillators are listed on [link]
- ✨Magic ✨  

## Install
To use this framework, you need to install [TA-lib] first. This lib is used for technical analysis functions. Installation guide could be found [here]. Python wrapper (project of [SomeHren]) is already included in framework and don't need to be installed separately. After getting TA-lib installed on your machine, type:
```sh
cd <desired-folder>
git clone <addr>
```



## Usage
here go explanations, comments, all that


## License

MIT

## Author

 Akim Mukhtarov [@akim_int80h]

**Free Software, Hell Yeah!**

[@akim_int80h]: <https://t.me/akim_int80h>
