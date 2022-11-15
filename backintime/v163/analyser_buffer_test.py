import typing as t

from itertools import chain
from datetime import datetime
from analyser import AnalyserBuffer, Value
from oscillators import OscillatorParam
from timeframes import Timeframes as tf 
from candle_properties import CandleProperties
from data import Candle


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


def prefetch_values(timeframe_meta) -> t.List[Value]: # or iterable?
    data = []
    for timeframe, meta in timeframe_meta.items():
        for candle_property, quantity in meta["candle_properties"].items():
            data.append(Value(timeframe=timeframe,
                              candle_property=candle_property,
                              quantity=quantity,
                              values=[]))   # fetch values here
    return data
    

def get_oscillators_params(strategy_t: t.Type) -> t.List[OscillatorParam]:
    params = map(lambda oscillator: oscillators.get_params(), 
                 strategy_t.oscillators)
    return list(chain.from_iterable(params))
    
    
params = [
    OscillatorParam(tf.H1, CandleProperties.CLOSE, 13),
    OscillatorParam(tf.H1, CandleProperties.CLOSE, 26),
    OscillatorParam(tf.H4, CandleProperties.OPEN, 9)
]
# oscillators_params = get_oscillators_params(params)
timeframes_meta = get_timeframes_meta(params)
base_timeframe = tf.H1
        
analyser_buffer = AnalyserBuffer(prefetch_values(timeframes_meta), 
                                 base_timeframe)

starts = [1000, 1500, 500, 1100]
candles = [
    Candle(open_time=datetime.utcnow(),
           open=starts[0] + i,
           high=starts[1] + i,
           low=starts[2] + i,
           close=starts[3] + i,
           volume=5000,
           close_time=datetime.utcnow())
                for i in range(1000, 27000, 1000)
]
ticks = 0

for candle in candles:
    analyser_buffer.update(candle, ticks)
    ticks += 1

for param in params:
    values = analyser_buffer.get(param.timeframe, param.candle_property, param.quantity)
    print(f"Values: {values}")
    print(f"Quantity: {len(values)}")