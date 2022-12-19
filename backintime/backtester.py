import typing as t

from datetime import datetime
from decimal import Decimal
from .trading_strategy import TradingStrategy
from .data.data_provider import (
    DataProvider, 
    DataProviderFactory,
    DataProviderError
)
from .analyser.analyser import Analyser
from .broker.base import BrokerException
from .broker.broker import Broker
from .broker.fees import FeesEstimator
from .broker_proxy import BrokerProxy
from .candles import Candles, CandlesBuffer
from .result import BacktestingResult
from .utils import validate_timeframes, prefetch_values


class Backtester:
    def __init__(self,
                 strategy_t: t.Type[TradingStrategy],
                 data_provider_factory: DataProviderFactory):
        validate_timeframes(strategy_t, data_provider_factory)
        self._strategy_t = strategy_t
        self._data_provider_factory = data_provider_factory

    def run(self, 
            start_money: t.Union[int, str],
            since: datetime, 
            until: datetime,
            maker_fee: str,
            taker_fee: str) -> BacktestingResult:
        # Create shared `Broker` for `BrokerProxy`
        fees = FeesEstimator(Decimal(maker_fee), Decimal(taker_fee))
        broker = Broker(Decimal(start_money), fees)
        broker_proxy = BrokerProxy(broker)
        # Create shared buffer for `Analyser`
        analyser_buffer = prefetch_values(self._strategy_t, 
                                          self._data_provider_factory, 
                                          since)
        analyser = Analyser(analyser_buffer, self._strategy_t.oscillators)
        # Create shared buffer for `Candles`
        timeframes = self._strategy_t.candle_timeframes
        candles_buffer = CandlesBuffer(since, timeframes)
        candles = Candles(candles_buffer)

        strategy = strategy_t(broker_proxy, analyser, candles)
        market_data = self._data_provider_factory.create(since, until)

        try:
            for candle in market_data:
                broker.update(candle)
                candles_buffer.update(candle)
                analyser_buffer.update(candle)
                strategy.tick()
        except (BrokerException, DataProviderError):
            # These are more or less expected, so don't terminate
            pass    # TODO: logging here

        return BacktestingResult(self._strategy_t.get_title(),
                                 market_data,
                                 start_money,
                                 broker.get_trades(),
                                 broker.get_orders())
