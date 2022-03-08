from typing import Union, Tuple, Iterable, TypeVar
from .oscillator_dependency import OscillatorDependency


_TIMEFRAME_IDX = 0
_OHLCV_PROPERTY_IDX = 1
_PERIOD_IDX = 2

def dependency(*deps) ->  Iterable[OscillatorDependency]:
    """ An utility used to create list of `OscillatorDependency`
        from some iterable. Just less verbose """

    return [
        OscillatorDependency(
            dep[_TIMEFRAME_IDX],
            dep[_OHLCV_PROPERTY_IDX],
            dep[_PERIOD_IDX]
        )
            for dep in deps
    ]
