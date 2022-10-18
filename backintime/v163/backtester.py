import typing as t

from itertools import chain
from datetime import datetime
from backintime.v163.trading_strategy import TradingStrategy
from backintime.v163.data.data_provider import DataProvider
from backintime.v163.exchange import Exchange
from backintime.v163.analyser import Analyser, AnalyserBuffer, Value
from backintime.v163.candles import Candles, CandlesBuffer


def get_timeframes_meta(params: t.Iterable[OscillatorParam]) -> dict:
    data = {}
    for param in params:
        tf = param.timeframe
        candle_property = param.candle_property
        tf_meta = data.get(tf, {})
        props = tf_meta.get("candle_properties", {})
        props[candle_property] = max(props.get(candle_property, 0),
                                     param.quantity)
        tf_meta["max_quantity"] = max(tf_meta.get("max_quantity", 0),
                                      param.quantity)
        if "candle_properties" not in tf_meta:
            tf_meta["candle_properties"] = props
        if tf not in data:
            data[tf] = tf_meta
    return data


def prefetch_values(timeframe_meta) -> t.List[Value]:
    data = []
    for timeframe, meta in timeframe_meta.items():
        for candle_property, quantity in meta["candle_properties"].items():
            data.append(Value(timeframe=timeframe,
                              candle_property=candle_property,
                              quantity=quantity,
                              values=[]))   # TODO: fetch values here
    return data
    

def get_oscillators_params(
        strategy_t: t.Type[TradingStrategy]) -> t.List[OscillatorParam]:
    params = map(lambda oscillator: oscillators.get_params(), 
                 strategy_t.oscillators)
    return list(chain.from_iterable(params))


class Backtester:
    def __init__(self, 
                 strategy_t: t.Type[TradingStrategy], 
                 market_data: DataProvider):
        self._strategy_t = strategy_t
        self._market_data = market_data

    def run(self, since: datetime, until: datetime):
        oscillators_params = get_oscillators_params(self._strategy_t)
        timeframes_meta = get_timeframes_meta(oscillator_params)
        base_timeframe = self._market_data.timeframe()
        
        analyser_buffer = AnalyserBuffer(prefetch_values(timeframes_meta), 
                                         base_timeframe)

        candles_buffer = CandlesBuffer(self._strategy_t.timeframes, 
                                       base_timeframe)
  
        exchange = Exchange(self._market_data)
        analyser = Analyser(self._strategy_t.oscillators, analyser_buffer)
        candles = Candles(candles_buffer)
        strategy = self._strategy_t(exchange, analyser, candles)
        ticks = 0

        for candle in exchange.candles():
            analyser_buffer.update(candle, ticks)
            candles_buffer.update(candle, ticks)
            strategy.tick()
            ticks += 1

        return exchange.get_trades() # wrap to instance with output methods
