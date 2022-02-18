# backtesting
✨ A framework for trading strategies backtesting with Python ✨  
**note**: as of current version trailing stop, stop limit and OCO
orders are not supported. Expected in 1.x.x releases.   

## Features
- Market/Limit orders management
- Use CSV or Binance API as a data source
- The same data can be represented in up to 16 timeframes
    (compression for shorter candles to imitate longer ones)
- Quick trading history statistics (win rate, avg. profit, etc.)
- Export trades to csv

## This is how it looks like - MACD strategy
[macd strategy explained]
```py
from backtesting import TradingStrategy, Timeframes
from backtesting.oscillators.macd import macd
'''
Extend TradingStrategy class and implement __call__ method
to have your own strategy
'''
class MacdStrategy(TradingStrategy):
    # declare required oscillators here for later use
    oscillators = ( macd(Timeframes.H4), )

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

[@akim_int80h]: <https://t.me/akim_int80h>
[macd strategy explained]: <https://www.investopedia.com/terms/m/macd.asp#:~:text=Moving%20average%20convergence%20divergence%20(MACD)%20is%20a%20trend%2Dfollowing,averages%20of%20a%20security's%20price.&text=Traders%20may%20buy%20the%20security,crosses%20below%20the%20signal%20line.>
