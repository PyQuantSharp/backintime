from abs import ABC, abstractmethod
from .oscillator import Oscillator


class OscillatorBuilder:
    @abstractmethod
    def build(self) -> Oscillator:
        pass
