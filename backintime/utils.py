import logging
import typing as t
from enum import Enum
from itertools import chain
from decimal import Decimal
from datetime import datetime, timedelta

from .trading_strategy import TradingStrategy
from .analyser.indicators.base import IndicatorParam
from .analyser.indicators.constants import CandleProperties
from .analyser.analyser import Analyser, AnalyserBuffer
from .broker.base import BrokerException
from .broker.broker import Broker
from .broker.fees import FeesEstimator
from .broker_proxy import BrokerProxy
from .candles import Candles, CandlesBuffer
from .result.result import BacktestingResult
from .timeframes import (
    Timeframes, 
    get_timeframes_ratio, 
    estimate_open_time, 
    estimate_close_time
)
from .data.data_provider import (
    DataProvider, 
    DataProviderFactory,
    DataProviderError
)


class PrefetchOptions(Enum):
    PREFETCH_SINCE = "PREFETCH_SINCE"
    PREFETCH_UNTIL = "PREFETCH_UNTIL"
    PREFETCH_NONE = "PREFETCH_NONE"


PREFETCH_SINCE = PrefetchOptions.PREFETCH_SINCE
PREFETCH_UNTIL = PrefetchOptions.PREFETCH_UNTIL
PREFETCH_NONE = PrefetchOptions.PREFETCH_NONE


def _get_indicators_params(
        strategy_t: t.Type[TradingStrategy]) -> t.List[IndicatorParam]:
    """Get list of all indicators params of the strategy."""
    return list(chain.from_iterable(strategy_t.indicators))


def _reserve_space(analyser_buffer: AnalyserBuffer, 
                   indicator_params: t.Iterable[IndicatorParam]) -> None:
    """Reserve space in `analyser_buffer` for all `indicator_params`."""
    for param in indicator_params:
        analyser_buffer.reserve(param.timeframe, 
                                param.candle_property,
                                param.quantity)


def _get_prefetch_count(base_timeframe: Timeframes, 
                        indicator_params: t.List[IndicatorParam]) -> int:
    """
    Get the number of `base_timeframe` candles needed to 
    prefetch all data for indicators. 
    """
    max_quantity = 0
    tf_quantity: t.Dict[Timeframes, int] = {}
    # Map timeframe to max quantity for that timeframe
    for param in indicator_params:
        tf_qty = tf_quantity.get(param.timeframe, 0)
        tf_quantity[param.timeframe] = max(tf_qty, param.quantity)
    # Scale quantity with timeframes ratio and find max
    for timeframe, quantity in tf_quantity.items():
        # NOTE: there must be no remainder
        tf_ratio, _ = get_timeframes_ratio(timeframe, base_timeframe)
        max_quantity = max(max_quantity, quantity*tf_ratio)

    return max_quantity


def prefetch_values(strategy_t: t.Type[TradingStrategy],
                    data_provider_factory: DataProviderFactory,
                    prefetch_option: PrefetchOptions,
                    start_date: datetime) -> t.Tuple[AnalyserBuffer, datetime]:
    # Префетч нужно всего один таймфрейм, конечно - меньший из всех
    # однако, число свеч должно быть таким, чтобы из нх можно было построить 
    # столько свеч самого старшего таймфрейма, сколько нужно
    base_timeframe = data_provider_factory.timeframe
    indicator_params = _get_indicators_params(strategy_t)

    if prefetch_option is PREFETCH_SINCE:
        # Prefetch values since `start_date`
        count = _get_prefetch_count(base_timeframe, indicator_params)
        analyser_buffer = AnalyserBuffer(start_date)
        _reserve_space(analyser_buffer, indicator_params)
        since = start_date
        until = estimate_open_time(since, base_timeframe, count)

        logger = logging.getLogger("backintime")
        logger.info("Start prefetching...")
        logger.info(f"count: {count}")
        logger.info(f"since: {since}")
        logger.info(f"until: {until}")

        data = data_provider_factory.create(since, until)
        for candle in data:
            analyser_buffer.update(candle)
        logger.info("Prefetching is done")
        return analyser_buffer, until

    elif prefetch_option is PREFETCH_UNTIL:
        # Prefetch values until `start_date`
        until = start_date
        count = _get_prefetch_count(base_timeframe, indicator_params)
        since = estimate_open_time(until, base_timeframe, -count)
        analyser_buffer = AnalyserBuffer(since)
        _reserve_space(analyser_buffer, indicator_params)

        logger = logging.getLogger("backintime")
        logger.info("Start prefetching...")
        logger.info(f"count: {count}")
        logger.info(f"since: {since}")
        logger.info(f"until: {until}")

        data = data_provider_factory.create(since, until)
        for candle in data:
            analyser_buffer.update(candle)
        logger.info("Prefetching is done")
        return analyser_buffer, until

    else:   # `PREFETCH_NONE` or any other
        # Don't prefetch
        analyser_buffer = AnalyserBuffer(start_date)
        _reserve_space(analyser_buffer, indicator_params)
        return analyser_buffer, start_date


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


UNTIL = PrefetchOptions.PREFETCH_UNTIL


def run_backtest(strategy_t: t.Type[TradingStrategy],
                 data_provider_factory: DataProviderFactory,
                 start_money: t.Union[int, str],
                 since: datetime, 
                 until: datetime,
                 maker_fee: str,
                 taker_fee: str,
                 prefetch_option: PrefetchOptions = UNTIL) -> BacktestingResult:
    """Run backtesting."""
    validate_timeframes(strategy_t, data_provider_factory)
    # Create shared `Broker` for `BrokerProxy`
    start_money = Decimal(start_money)
    fees = FeesEstimator(Decimal(maker_fee), Decimal(taker_fee))
    broker = Broker(start_money, fees)
    broker_proxy = BrokerProxy(broker)
    # Create shared buffer for `Analyser`
    analyser_buffer, since = prefetch_values(strategy_t, 
                                             data_provider_factory,
                                             prefetch_option,
                                             since)
    analyser = Analyser(analyser_buffer)
    # Create shared buffer for `Candles`
    timeframes = strategy_t.candle_timeframes
    candles_buffer = CandlesBuffer(since, timeframes)
    candles = Candles(candles_buffer)

    strategy = strategy_t(broker_proxy, analyser, candles)
    market_data = data_provider_factory.create(since, until)
    logger = logging.getLogger("backintime")
    logger.info("Start backtesting...")

    try:
        for candle in market_data:
            broker.update(candle)           # Review whether orders can be executed
            candles_buffer.update(candle)   # Update candles on required timeframes
            analyser_buffer.update(candle)  # Store data for indicators calculation
            strategy.tick()                 # Trading strategy logic here

    except (BrokerException, DataProviderError) as e:
        # These are more or less expected, so don't raise
        name = e.__class__.__name__
        logger.error(f"{name}: {str(e)}\nStop backtesting...")

    logger.info("Backtesting is done")
    return BacktestingResult(strategy_t.get_title(),
                             market_data,
                             start_money,
                             broker.balance.fiat_balance,
                             broker.current_equity,
                             broker.get_trades(),
                             broker.get_orders())