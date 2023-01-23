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

#### Backtesting

Backtesting is done in `run_backtest` function, which basically initializes required objects, 
prefetches market data if needed and runs the similar loop:

```py
for candle in candles:
    broker.update(candle)   # Review whether orders can be executed
    analyser.update(candle) # Store data for indicators calculation
    candles.update(candle)  # Update candles on required timeframes
    strategy.tick()         # Trading strategy logic here
```


#### TradingStrategy

Base class for trading strategies. 
Strategy must provide algorithm implementation in `tick` method, which runs each time a new candle closes.


#### Broker

Broker provides orders management in a simulated market environment. 
The broker executes/activates orders whose conditions fits the market. 
Supports Market, Limit, Take Profit, Take Profit Limit, Stop Loss, Stop Loss Limit orders.
Order execution policy of builtin broker:

- **Market orders**: 
	All market orders will be executed when a new candle closes. 
	The price of execution is the candle's OPEN price.

- **Limit orders**: 
    Each of the conditions from the following list will in turn be applied to the `order_price` of each order:
		```
        1) price == candle.OPEN
        2) price >= candle.LOW and price <= candle.HIGH
        3) price == candle.CLOSE
		```
    The order will be executed if the condition is true. 
    The price of execution is the order's `order_price`.

- **Take Profit/Stop Loss orders**: 
    The activation conditions are essentially the same as for limit orders, but the conditions from the list are applied to order's `trigger_price`. 
    When a TP/SL order is triggered, it will be treated as a market or limit order, depending on whether `order_price` is set for the order. 


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


#### Prefetching

Indicators require a certain amount of data to get a correct result. For example, to calculate the SMA (simple moving average) with a period of 9, 9 values are required. 
So, the strategy will get the wrong result of the SMA indicator, until all 9 candles are accumulated.  

In order for the strategy to get the correct values right from the start, prefetching of market data is used. You can configure this behavior by choosing from the following options and passing it as `prefetch_option` argument to the `run_backtest` function:
- **PREFETCH_UNTIL** (default) - prefetch the required amount of data until `since` date; the amount of data required is calculated automatically. In this case, the strategy backtesting will be started from the `since` date. This option is convenient when market data is requested from the exchange API, because situations when the exchange does not have enough historical data are quite rare. 

- **PREFETCH_SINCE** - prefetch the required amount of data from `since` date; the amount of data required for this is calculated automatically. In this case, the strategy backtesting will be launched starting from the dynamically calculated date. This option may be useful when working with a CSV file when you are not sure if it contains enough data before the `since` date. 

- **PREFETCH_NONE** - Do not prefetch data.  

Where `since` date is the value of the argument `since` passed to the `run_backtest` function. 


## Docs

There is no documentation yet because the code is unstable. As for now, you can browse sources or type `help` in REPL. 


## License

MIT


## Author

 Akim Mukhtarov [@akim_int80h]


[@akim_int80h]: <https://t.me/akim_int80h>
[macd strategy explained]: <https://www.investopedia.com/terms/m/macd.asp#:~:text=Moving%20average%20convergence%20divergence%20(MACD)%20is%20a%20trend%2Dfollowing,averages%20of%20a%20security's%20price.&text=Traders%20may%20buy%20the%20security,crosses%20below%20the%20signal%20line.>
