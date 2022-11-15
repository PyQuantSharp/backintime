# backintime 1.6.3
✨ A framework for trading strategies backtesting with Python ✨  
> Branch for the new version (not yet released). 
  In this version, I'll implement trailing stop and stop loss orders, fix bugs,
  rewrite internals in a more clear and OOP way and improve type hints in all package  
  Note: as for now, this is neither stable nor working code.   

## Features
- Market, limit, take profit, stop loss orders management
- Use CSV or Binance API as a data source
- The same data can be represented in up to 16 timeframes  
    (few short candles is compressed to longer one)
- Brief trading history statistics (win rate, avg. profit, etc.)
- Export trades to csv


## License

MIT

## Author

 Akim Mukhtarov [@akim_int80h]


[@akim_int80h]: <https://t.me/akim_int80h>
[macd strategy explained]: <https://www.investopedia.com/terms/m/macd.asp#:~:text=Moving%20average%20convergence%20divergence%20(MACD)%20is%20a%20trend%2Dfollowing,averages%20of%20a%20security's%20price.&text=Traders%20may%20buy%20the%20security,crosses%20below%20the%20signal%20line.>
