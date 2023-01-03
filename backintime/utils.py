import typing as t
import logging
from itertools import chain
from datetime import datetime, timedelta

from .analyser.analyser import AnalyserBuffer
from .analyser.indicators.base import IndicatorParam
from .analyser.indicators.constants import CandleProperties
from .data.data_provider import DataProviderFactory
from .timeframes import Timeframes, get_timeframes_ratio
from .trading_strategy import TradingStrategy


logger = logging.getLogger("backintime")


def _get_indicators_params(
        strategy_t: t.Type[TradingStrategy]) -> t.List[IndicatorParam]:
    """Get list of all indicators params of the strategy."""
    params = map(lambda x: x.indicator_params, 
                 strategy_t.indicators)
    return list(chain.from_iterable(params))


DEFAULT_PREFETCH_COUNT = 100    # ?
MAGIC_PREFETCH_CONSTANT = 6     # ?


def _get_prefetch_count(base_timeframe: Timeframes, 
                        indicator_params: t.List[IndicatorParam]) -> int:
    """
    Get the number of `base_timeframe` candles needed to 
    prefetch all data for indicators. 
    """
    max_timeframe = base_timeframe
    max_quantity = 1

    for param in indicator_params:
        if param.timeframe.value > max_timeframe.value:
            max_timeframe = param.timeframe
            if param.quantity and param.quantity > max_quantity:
                max_quantity = param.quantity
    # NOTE: there must be no remainder
    timeframes_ratio, _ = get_timeframes_ratio(max_timeframe, base_timeframe)
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
    indicator_params = _get_indicators_params(strategy_t)
    required_count = _get_prefetch_count(base_timeframe, indicator_params)
    since = until - timedelta(seconds=required_count * base_timeframe.value)
    # TODO: implement optional prefetching
    logger.info("Start prefetching...")
    logger.info(f"required count: {required_count}")
    logger.info(f"since: {since}")
    logger.info(f"until: {until}")

    analyser_buffer = AnalyserBuffer(since)
    for param in indicator_params:
        timeframes_ratio, _ = get_timeframes_ratio(param.timeframe, 
                                                   base_timeframe)
        quantity = int(required_count / timeframes_ratio)
        analyser_buffer.reserve(param.timeframe, 
                                param.candle_property,
                                quantity)

    data_provider = data_provider_factory.create(since, until)
    for candle in data_provider:
        analyser_buffer.update(candle)
    logger.info("Prefetching is done")
    return analyser_buffer


class IncompatibleTimeframe(Exception):
    def __init__(self, 
                 timeframe: Timeframes, 
                 incompatibles: t.Iterable[Timeframes], 
                 strategy_t: t.Type[TradingStrategy]):
        message = (f"Input candles timeframe is {timeframe} which can\'t be "
                   f"used to represent timeframes: {incompatibles} "
                   f"(required for `{strategy_t}` "
                   f"aka `{strategy_t.get_title()}`)")
        super().__init__(message)


def validate_timeframes(strategy_t: t.Type[TradingStrategy],
                        data_provider_factory: DataProviderFactory) -> None:
    """
    Check whether all timeframes required for `strategy_t` can be
    represented by candlesticks from data provider.
    """
    indicator_params = _get_indicators_params(strategy_t)
    indicator_timeframes = { x.timeframe for x in indicator_params }
    candle_timeframes = strategy_t.candle_timeframes
    timeframes = indicator_timeframes | candle_timeframes
    base_timeframe = data_provider_factory.timeframe
    # Timeframes are incompatible if there is non zero remainder
    is_incompatible = lambda tf: get_timeframes_ratio(tf, base_timeframe)[1]
    incompatibles = list(filter(is_incompatible, timeframes))
    if incompatibles:
        raise IncompatibleTimeframe(base_timeframe, 
                                    incompatibles, strategy_t)
