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
class MacdStrategy(TradingStrategy):

    oscillators = ( MACD(Timeframes.H4), )

    def __call__(self):
        macd = self._oscillators.get('MACD_H4')
        if not self.position and macd.crossover_up():
            self._buy()
        elif self.position and macd.crossover_down():
            self._sell()
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

[@akim_int80h]: <https://t.me/akim_int80h>
