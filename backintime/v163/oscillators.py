import typing as t
from abc import ABC, abstractmethod


class CandleProperties:
	pass


@dataclass
class Param:
	candle_property: CandleProperties
	size: int


class Oscillator(ABC):
	@abstractmethod
	def get_name(self) -> str:
		pass

	@abstractmethod
	def get_params(self) -> t.Dict[str, Param]:
		pass

	@abstractmethod
	def __call__(self, **kwargs) -> t.Any:
		pass
