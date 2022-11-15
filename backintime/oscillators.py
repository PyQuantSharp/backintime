import typing as t

from abc import ABC, abstractmethod
from dataclasses import dataclass
from backintime.v163.timeframes import Timeframes
from backintime.v163.candle_properties import CandleProperties


@dataclass
class OscillatorParam:
    timeframe: Timeframes
    candle_property: CandleProperties
    quantity: int


class Oscillator(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_params(self) -> t.Dict[str, OscillatorParam]:
        pass

    @abstractmethod
    def __call__(self, **kwargs) -> t.Any:
        pass
