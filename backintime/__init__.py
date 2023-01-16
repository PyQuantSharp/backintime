"""
✨ Tool for testing trading strategies on historical data ✨    
Such testing does not guarantee the same results in real trading, 
but it gives a rough estimate of a strategy's success.
The smaller timeframe is used, the more accurate the results will be.
Short overview of the core concepts is given below.


Backtester

Test trading strategy on historical data.
`strategy_t` designates which strategy to test, 
and `data_provider_factory` - which data to use.


TradingStrategy

Base class for trading strategies. 
Strategy must provide algorithm implementation in `tick` method, 
which runs each time a new candle closes.


Broker

Broker provides orders management in a simulated
market environment. The broker executes/activates orders
whose conditions fits the market. Supports Market, Limit,
Take Profit, Take Profit Limit, Stop Loss, Stop Loss Limit orders.


Analyser

Indicators calculation.
Supported indicators:
    - MA - Moving Average
    - EMA - Exponential Moving Average
    - MACD - Moving Average Convergence Divergence
    - BBANDS - Bollinger Bands
    - RSI - Relative Strength Index
    - ATR - Average True Range
    - ADX - Average Directional Movement Index
    - DMI - Directional Movement Indicator
    - PIVOT - Pivot Points (Traditional, Fibonacci or Classic)


Candles

Provides the last candle representation for various timeframes.
It is useful for checking properties of a candle 
on one timeframe (H1, for example), while having data
on another (for instance, M1).


DataProvider

Provides candles in historical order.
`DataProvider` is an iterable object that 
can be created for specific date range (since, until);
Yields OHLCV candle during iteration.


BacktestingResult

Provides export to CSV and stats such as Win Rate, Profit/Loss,
Average Profit, Best/Worst deal etc.
Supports estimation in FIFO (First-In-First-Out), 
LIFO (Last-In-First-Out) or AVCO (Average Cost) algorithms.
The algorithm name specifies the order in which BUYs
must be considered to estimate profit or loss.

All these algorithms produce the same result if SELL
order always follows only one BUY.
"""
import logging
from .backtester import Backtester
from .trading_strategy import TradingStrategy


logging.basicConfig(level='INFO')
