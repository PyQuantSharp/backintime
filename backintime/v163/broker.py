from abc import abstractmethod, ABC


class Broker(ABC):
	""" """
	@abstractmethod
	def submit_order(self) -> None:
		""" Submit order """
		pass

	@abstractmethod
	def get_accounts(self) -> float:
		pass

	@abstractmethod
	def get_trades(self) -> list:
		pass