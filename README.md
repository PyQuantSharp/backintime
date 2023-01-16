# backintime 1.6.3
✨ Tool for testing trading strategies on historical data ✨    
Such testing does not guarantee the same results in real trading, but it gives a rough estimate of a strategy's success.
The smaller timeframe is used, the more accurate the results will be.

> Branch for the new version (not yet released). 
  In this version, I'll implement take profit and stop loss orders, fix bugs,
  rewrite internals in a more clear and OOP way and improve type hints in all package  
  Note: Margin trading is not supported as for now. Expected in 2.x releases.

## Features
- Use CSV or Binance API as a data source
- The same data can be represented in various timeframes  
    (few short candles is used to represent longer one)
- Market, Limit, Take Profit, Take Profit Limit, Stop Loss, Stop Loss Limit orders management
- Builtin indicators. See [list](#indicators).
- Trading statistics (win rate, profit/loss, avg. profit, etc.) with FIFO, LIFO or AVCO Profit/Loss estimation algorithms
- Export orders, trades and statistics to csv


## Indicators
- MA - Moving Average
- EMA - Exponential Moving Average
- MACD - Moving Average Convergence Divergence
- BBANDS - Bollinger Bands
- RSI - Relative Strength Index
- ATR - Average True Range
- ADX - Average Directional Movement Index
- DMI - Directional Movement Indicator
- PIVOT - Pivot Points (Traditional, Fibonacci or Classic)


## Core concepts

Backtesting is done in `Backtester.run` method, which basically initializes required objects, 
prefetches market data if needed and runs the similar loop:

```py
for candle in candles:
    broker.update(candle)   # Review whether orders can be executed
    analyser.update(candle) # Store data for indicators calculation
    candles.update(candle)  # Update candles on required timeframes
    strategy.tick()         # Trading strategy logic here
```
Short overview of the core concepts is given below.


#### Backtester

Test trading strategy on historical data.
`strategy_t` designates which strategy to test, and `data_provider_factory` - which data to use.


#### TradingStrategy

Base class for trading strategies. 
Strategy must provide algorithm implementation in `tick` method, which runs each time a new candle closes.


#### Broker

Broker provides orders management in a simulated market environment. 
The broker executes/activates orders whose conditions fits the market. 
Supports Market, Limit, Take Profit, Take Profit Limit, Stop Loss, Stop Loss Limit orders.


#### Analyser

Indicators calculation. See [list](#indicators) of supported indicators.


#### Candles

Provides the last candle representation for various timeframes.
It is useful for checking properties of a candle on one timeframe (H1, for example), while having data on another (for instance, M1).


#### DataProvider

Provides candles in historical order.
`DataProvider` is an iterable object that can be created for specific date range (since, until); 
Yields OHLCV candle during iteration.


#### BacktestingResult

Provides export to CSV and stats such as Win Rate, Profit/Loss, Average Profit, Best/Worst deal, etc.
Supports estimation in FIFO (First-In-First-Out), LIFO (Last-In-First-Out) or AVCO (Average Cost) algorithms.
The algorithm name specifies the order in which BUYs must be considered to estimate profit or loss.
All these algorithms produce the same result if SELL order always follows only one BUY.


## License

MIT


## Docs

There is no documentation yet because the code is unstable. As for now, you can browse sources or type `help` in REPL. 


## Author

 Akim Mukhtarov [@akim_int80h]


[@akim_int80h]: <https://t.me/akim_int80h>
[macd strategy explained]: <https://www.investopedia.com/terms/m/macd.asp#:~:text=Moving%20average%20convergence%20divergence%20(MACD)%20is%20a%20trend%2Dfollowing,averages%20of%20a%20security's%20price.&text=Traders%20may%20buy%20the%20security,crosses%20below%20the%20signal%20line.>
