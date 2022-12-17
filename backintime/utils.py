import typing as t
from itertools import chain
from datetime import datetime, timedelta

from .analyser.analyser import AnalyserBuffer
from .analyser.oscillators.base import OscillatorParam
from .analyser.oscillators.constants import CandleProperties
from .data.data_provider import DataProviderFactory
from .timeframes import Timeframes
from .trading_strategy import TradingStrategy


def _get_oscillators_params(
        strategy_t: t.Type[TradingStrategy]) -> t.List[OscillatorParam]:
    """Get list of all oscillator params of the strategy."""
    params = map(lambda x: x.get_oscillator_params(), 
                 strategy_t.oscillators)
    return list(chain.from_iterable(params))


DEFAULT_PREFETCH_COUNT = 100    # ?
MAGIC_PREFETCH_CONSTANT = 6     # ?


def _get_prefetch_count(base_timeframe: Timeframes, 
                        oscillator_params: t.List[OscillatorParam]) -> int:
    """
    Get the number of `base_timeframe` candles needed to 
    prefetch all data for oscillators. 
    """
    max_timeframe = base_timeframe
    max_quantity = 1

    for param in oscillator_params:
        if param.timeframe.value > max_timeframe.value:
            max_timeframe = param.timeframe
            if param.quantity and param.quantity > max_quantity:
                max_quantity = param.quantity
    # NOTE: there must be no remainder
    timeframes_ratio = max_timeframe.value//base_timeframe.value
    quantity = timeframes_ratio * max_quantity
    quantity = max(DEFAULT_PREFETCH_COUNT, 
                   max_quantity*MAGIC_PREFETCH_CONSTANT)
    return quantity * timeframes_ratio


def prefetch_values(strategy_t: t.Type[TradingStrategy],
                    data_provider_factory: DataProviderFactory,
                    until: datetime) -> AnalyserBuffer:
    # Префетч нужно всего один таймфрейм, конечно - меньший из всех
    # однако, число свеч должно быть таким, чтобы из нх можно было построить 
    # столько свеч самого старшего таймфрейма, сколько нужно
    base_timeframe = data_provider_factory.timeframe
    oscillator_params = _get_oscillators_params(strategy_t)
    required_count = _get_prefetch_count(base_timeframe, oscillator_params)
    since = until - timedelta(seconds=required_count * base_timeframe.value)
    #
    print(f"required count: {required_count}")
    print(f"since: {since}")
    print(f"until: {until}")
    #
    analyser_buffer = AnalyserBuffer(since)
    for param in oscillator_params:
        timeframes_ratio = param.timeframe.value / base_timeframe.value
        quantity = int(required_count / timeframes_ratio)
        analyser_buffer.reserve(param.timeframe, 
                                param.candle_property,
                                quantity)

    data_provider = data_provider_factory.create(since, until)
    for candle in data_provider:
        analyser_buffer.update(candle)
    return analyser_buffer


class IncompatibleTimeframe(Exception):
    def __init__(self, 
                 timeframe: Timeframes, 
                 incompatibles: t.Iterable[Timeframes], 
                 strategy_t: t.Type[TradingStrategy]):
        message = (f"Input candles timeframe is {timeframe} which can\'t be "
                   f"used to represent timeframes: {incompatibles} "
                   f"(required for `{strategy_t.__name__})`")
        super().__init__(message)


def validate_timeframes(strategy_t: t.Type[TradingStrategy],
                        data_provider_factory: DataProviderFactory) -> None:
    """
    Check whether all timeframes required for `strategy_t` can be
    represented by candlesticks from data provider.
    """
    oscillator_params = _get_oscillators_params(strategy_t)
    oscillator_timeframes = { x.timeframe for x in oscillator_params }
    candle_timeframes = strategy_t.timeframes
    timeframes = oscillator_timeframes | candle_timeframes
    base_timeframe = data_provider_factory.timeframe

    is_incompatible = lambda tf: tf.value % base_timeframe.value
    incompatibles = list(filter(is_incompatible, timeframes))
    if incompatibles:
        raise IncompatibleTimeframe(base_timeframe, 
                                    incompatibles, strategy_t)
