# backintime 1.6.3
✨ Tool for testing trading strategies on historical data ✨    
Such testing does not guarantee the same results in real trading, but it gives a rough estimate of a strategy's success.
The smaller timeframe is used, the more accurate the results will be.

> Note: Margin trading is not supported as for now. Expected in 2.x releases.


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


## Installation
```sh
python3 -m pip install backintime
```


## How to use

Sample with MACD strategy is provided below. The strategy buys when the MACD line crosses from below to above the signal line, (i.e. histogram becomes non-zero), and sells when MACD line crosses from above to below the signal line. Note that this strategy results in a high losses and only provided as a reference. Generally no one uses only one indicator in a trading strategy. 
```py
from datetime import datetime
from backintime import TradingStrategy, run_backtest
from backintime.trading_strategy import TradingStrategy
from backintime.timeframes import Timeframes as tf
from backintime.indicator_params import MACD
from backintime.data.binance import BinanceCandlesFactory


class MacdStrategy(TradingStrategy): # (1)
    title = "Sample MACD Strategy"
    indicators = { MACD(tf.H1) }	# (2)

    def tick(self):	# (3)
        macd = self.analyser.macd(tf.H1)
        if not self.position and macd.crossover_up():
            self.buy()	# (4)
        elif self.position and macd.crossover_down():
            self.sell()	# (5)


feed = BinanceCandlesFactory('BTCUSDT', tf.M15)	# (6)
since = datetime.fromisoformat("2020-01-01 00:00+00:00")
until = datetime.fromisoformat("2021-01-01 00:00+00:00")

result = run_backtest(MacdStrategy, feed,
                      10_000, since, until, 
                      maker_fee='0.005', taker_fee='0.005')
print(result)
print(result.get_stats('FIFO'))
result.export()
```
To implement a strategy, you need to create a class derived from `TradingStrategy` (1), specify which indicators is used (2) and provide algorithm implementation in `tick` method (3). 
When the corresponding conditions are met, the strategy calls `buy` (4) or `sell` (5) methods, which are aliases for Market order submission.
Here the backtesting is done with candlesticks from Binance API on 15 minutes timeframe (6). However, consider using CSV file instead for better performance.

---

The following sample with "SMA resistance breakout" strategy demonstrates more 
advanced features: Limit orders, Take Profit and Stop Loss. 
The strategy buys when the last close crosses from below to above SMA line and 
sells at Take Profit or Stop Loss levels. MACD and DMI signals are used as filters.
```py
import typing as t
from datetime import datetime
from decimal import Decimal
from backintime import TradingStrategy, run_backtest
from backintime.timeframes import Timeframes as tf
from backintime.data.binance import BinanceCandlesFactory
from backintime.indicator_params import SMA, MACD, DMI, PIVOT
from backintime.analyser.indicators.dmi import DMIResultSequence
from backintime.analyser.indicators.macd import MacdResultSequence
from backintime.broker import TakeProfitOptions, StopLossOptions


def macd_hist_up(macd: MacdResultSequence) -> bool:
    """True, if MACD hist > 0."""
    return macd[-1].hist > 0


def dmi_buy_signal(dmi: DMIResultSequence) -> bool:
    """True, if +DI > -DI."""
    return dmi.positive_di[-1] > dmi.negative_di[-1]


class SmaResistanceBreakout(TradingStrategy):
    title = "SMA resistance breakout"
    candle_timeframes = { tf.M15 }
    indicators = {
        SMA(tf.M15, 55),
        MACD(tf.M15),
        DMI(tf.M15, 14),
        PIVOT(tf.D1, 15)
    }

    def __init__(self, broker, analyser, candles):
        self.prev_close: t.Optional[Decimal] = None
        self.curr_close: t.Optional[Decimal] = None
        super().__init__(broker, analyser, candles)

    def tick(self):
        self.prev_close = self.curr_close
        self.curr_close = self.candles.get(tf.M15).close
        sma = self.analyser.sma(tf.M15, period=55)[-1]
        sma_crossover_up = self.curr_close > sma and \
                           self.prev_close and self.prev_close <= sma

        if self.broker.max_fiat_for_maker and sma_crossover_up and \
                macd_hist_up(self.analyser.macd(tf.M15)) and \
                dmi_buy_signal(self.analyser.dmi(tf.M15, 14)):
            # Calculate buy price: current SMA + 0.2%
            limit_price = Decimal(sma) * Decimal('1.002')
            # Set up TP at PIVOT' R2 level
            pivot = self.analyser.pivot(tf.D1, 15)
            take_profit_trigger = pivot[-1].r2
            take_profit = TakeProfitOptions(percentage_amount=Decimal('100.00'),
                                            trigger_price=take_profit_trigger)
            # Set up SL at current close price - 5%
            stop_loss_trigger = self.candles.get(tf.M15).close * Decimal('0.95')
            stop_loss = StopLossOptions(percentage_amount=Decimal('100.00'), 
                                        trigger_price=stop_loss_trigger)
            # Submit limit buy with TP & SL
            self.limit_buy(order_price=limit_price,
                           amount=self.broker.max_fiat_for_maker,
                           take_profit=take_profit,
                           stop_loss=stop_loss)


feed = BinanceCandlesFactory('BTCUSDT', tf.M15)
since = datetime.fromisoformat("2020-03-01 00:00+00:00")
until = datetime.fromisoformat("2021-05-01 00:00+00:00")

result = run_backtest(SmaResistanceBreakout, feed, 
                      10_000, since, until, 
                      maker_fee='0.005', taker_fee='0.005')

print(result)
print(result.get_stats('FIFO'))
print(result.get_stats('LIFO'))
print(result.get_stats('AVCO'))
result.export()

```

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
    All market orders will be executed 
    when a new candle closes.
    The price of execution is the candle's OPEN price.

- **Limit orders**: 
	Limit order will be executed at the limit price or better:
    lower or equal price for BUY orders and higher or equal price 
    for SELL orders.
    First, the `order_price` of each order will be compared to
    the OPEN price of a new candle:
    ```
    BUY orders will be executed if `order_price` >= OPEN. 
    SELL orders will be executed if `order_price` <= OPEN.
   	```
    Then, remaining BUYs will be compared to LOW,
    and remaining SELLs - to HIGH.
    Fill price is the first price that matched limit price.

- **Take Profit/Stop Loss orders**:  
	TP/SL orders will be activated if the `trigger_price` is
    within the price bounds of a candle.
    This check is performed in two steps:
    ```    
	1) For each order: activate if trigger_price == OPEN
    2) For each order: activate if LOW <= trigger_price <= HIGH
    ``` 
    When a TP/SL order is triggered, it will be treated
    as a market or limit order, depending on whether
 	`order_price` is set for the order.

Limit, Take Profit and Stop Loss orders are reviewed
in the order of their submission (oldest first).



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


## Some thoughts

I plan to add support for margin trading (will allow testing of short and leveraged strategies) 
and implement backtesting as an event based system using a queue for communication 
(will allow running backtesting on distributed systems).


## Docs

There is no documentation yet because the code is unstable (but works). As for now, you can browse sources or type `help` in REPL. 


## License

MIT


## Author

 Akim Mukhtarov [@akim_int80h]


[@akim_int80h]: <https://t.me/akim_int80h>