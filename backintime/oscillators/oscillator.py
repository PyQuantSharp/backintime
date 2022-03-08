from typing import TypeVar, Iterable, Any
from abc import ABC, abstractmethod

from .oscillator_dependency import OscillatorDependency
from ..market_data_storage import MarketDataStorage


DEFAULT_LOOKUP = 300

OscillatorDependencies_t = TypeVar(
        "OscillatorDependencies", bound=Iterable[OscillatorDependency])

class Oscillator(ABC):
    """
    Base class for all oscillators.
    Implement __call__ and reserve methods
    to have your own oscillator
    """
    def __init__(
            self,
            deps: OscillatorDependencies_t,
            market_data: MarketDataStorage,
            name: str
    ):
        """ :param:`deps` is used to reserve lookup space
                and track required OHLC values.
                see :class:`MarketDataStorage` for implementation details
            :param:`market_data` is a data storage
                where it can be obtained
            :param:`name` is used to access oscillator value
                from :class:`MarketDataAnalyzer` """
        self._name = name
        self._market_data = market_data
        self._deps = deps
        self._reserve()

    def get_name(self) -> str:
        return self._name

    def _get_values(self):
        """ Returns up-to-date OHLC values that was
            reserved via `deps` declaration """
        values = [
            self._market_data.get(
                dep.timeframe,
                dep.ohlcv_property,
                dep.period
            )
                for dep in self._deps
        ]
        return values if len(values) > 1 else values[0]

    def _reserve(self):
        """ Reserves lookup space for oscillator arguments """
        for dep in self._deps:
            self._market_data.reserve(
                dep.timeframe,
                dep.ohlcv_property,
                dep.period)

    @abstractmethod
    def __call__(self) -> Any:
        """ Runs each time a new candle closes
            Should return an up-to-date oscillator' value """
        pass
