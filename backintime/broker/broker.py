import typing as t
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .orders import OrderFactory, OrderInfo


@dataclass
class BalanceData:
    fiat_balance: float
    available_fiat_balance: float
    crypto_balance: float
    available_crypto_balance: float


class Balance:
    def __init__(self, data: BalanceData):
        self._data = data

    @property
    def available_fiat_balance(self) -> float:
        return self._data.available_fiat_balance

    @property
    def available_crypto_balance(self) -> float:
        return self._data.available_crypto_balance
    
    @property
    def fiat_balance(self) -> float:
        return self._data.fiat_balance

    @property
    def crypto_balance(self) -> float:
        return self._data.crypto_balance


class AbstractBroker(ABC):
    @abstractmethod
    def get_balance(self) -> Balance:
        pass
    
    @abstractmethod
    def get_fiat_balance(self) -> float:
        pass
    
    @abstractmethod
    def get_crypto_balance(self) -> float:
        pass

    @abstractmethod
    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        pass

    @abstractmethod
    def cancel_order(self, order) -> None:
        pass


class Broker(AbstractBroker):
    def get_balance(self) -> Balance:
        pass
    
    def get_fiat_balance(self) -> float:
        pass
    
    def get_crypto_balance(self) -> float:
        pass
    
    def submit_order(self, order_factory: OrderFactory) -> OrderInfo:
        pass

    def cancel_order(self, order) -> None:
        pass