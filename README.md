# backintime 1.6.3
✨ Tool for testing trading strategies on historical data ✨    
Such testing does not guarantee the same results in real trading, but it gives a rough estimate of a strategy's success and allows you to quickly check the effect of changes. 
The smaller timeframe is used, the more accurate the results will be.

> Branch for the new version (not yet released). 
  In this version, I'll implement trailing stop and stop loss orders, fix bugs,
  rewrite internals in a more clear and OOP way and improve type hints in all package  
  Note: Margin trading is not supported as for now. Expected in 2.x releases.

## Features
- Use CSV or Binance API as a data source
- The same data can be represented in various timeframes  
    (few short candles is used to represent longer one)
- Market, Limit, Take Profit, Take Profit Limit, Stop Loss, Stop Loss Limit orders management
- Builtin support for MA, EMA, MACD, BBANDS, RSI, ATR, ADX, DMI
- Trading statistics (win rate, profit/loss, avg. profit, etc.) with FIFO, LIFO or ACVO Profit/Loss estimation algorithms
- Export orders, trades and statistics to csv


## License

MIT

## Author

 Akim Mukhtarov [@akim_int80h]


[@akim_int80h]: <https://t.me/akim_int80h>
[macd strategy explained]: <https://www.investopedia.com/terms/m/macd.asp#:~:text=Moving%20average%20convergence%20divergence%20(MACD)%20is%20a%20trend%2Dfollowing,averages%20of%20a%20security's%20price.&text=Traders%20may%20buy%20the%20security,crosses%20below%20the%20signal%20line.>
