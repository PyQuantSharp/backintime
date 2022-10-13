# Backintime 1.6.3

## Ideas about new version:  
- Implement trailing stop and stop loss orders 
- Add builtin support for other exchanges (OKX?) 
- Rewrite internals in a more clear and OOP way  
- Improve type hints in all package 

## Implementation tweaks:
- Rewrite candles providers implementing `Iterator` and `Generator`  
- In `TradingStrategy` change `__call__` method to `tick` to emphasise the expected event 
- Make `Oscillator` stateless, instead pass all required data to `__call__` method 
- Change dates accepted by `Backtester` to `datetime` (instead of `str` in ISO format) 
- Update buffers for timeframe candles and oscillators in `Backtester.run`  
- Remove redundant `TickCounter` and keep tracking ticks in `Backtester.run`  
- Remove last run state from `Backtester` and return results right from `run` method 
- Add `get_accounts`, `get_trades` to `Broker` 