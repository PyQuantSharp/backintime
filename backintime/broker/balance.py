import typing as t
from decimal import Decimal   # https://docs.python.org/3/library/decimal.html
from .base import AbstractBalance, InsufficientFunds


class Balance(AbstractBalance):
    """Default balance implementation for default broker."""
    def __init__(self, 
                 fiat_balance: Decimal, 
                 crypto_balance: t.Optional[Decimal] = Decimal(0)):
        self._fiat_balance = fiat_balance
        self._available_fiat_balance = fiat_balance
        self._crypto_balance = crypto_balance
        self._available_crypto_balance = crypto_balance

    @property
    def available_fiat_balance(self) -> Decimal:
        """Get fiat available for trading."""
        return self._available_fiat_balance

    @property
    def available_crypto_balance(self) -> Decimal:
        """Get crypto available for trading."""
        return self._available_crypto_balance
    
    @property
    def fiat_balance(self) -> Decimal:
        """Get fiat balance."""
        return self._fiat_balance

    @property
    def crypto_balance(self) -> Decimal:
        """Get crypto balance."""
        return self._crypto_balance

    def hold_fiat(self, amount: Decimal) -> None:
        """
        Ensure there are enough fiat available for trading and
        and decrease it.
        """
        if amount > self._available_fiat_balance:
            raise InsufficientFunds()
        self._available_fiat_balance -= amount

    def hold_crypto(self, amount: Decimal) -> None:
        """
        Ensure there are enough crypto available for trading and
        and decrease it.
        """
        if amount > self._available_crypto_balance:
            raise InsufficientFunds()
        self._available_crypto_balance -= amount

    def release_fiat(self, amount: Decimal) -> None:
        """Increase fiat available for trading."""
        self._available_fiat_balance += amount

    def release_crypto(self, amount: Decimal) ->  None:
        """Increase crypto available for trading."""
        self._available_crypto_balance += amount

    def withdraw_fiat(self, amount: Decimal) -> None:
        """Decrease fiat balance."""
        self._fiat_balance -= amount

    def withdraw_crypto(self, amount: Decimal) -> None:
        """Decrease crypto balance."""
        self._crypto_balance -= amount

    def deposit_fiat(self, amount: Decimal) -> None:
        """Increase fiat balance and the amount available for trading."""
        self._fiat_balance += amount
        self._available_fiat_balance += amount

    def deposit_crypto(self, amount: Decimal) -> None:
        """Increase crypto balance and the amount available for trading."""
        self._crypto_balance += amount
        self._available_crypto_balance += amount

    def __repr__(self) -> str:
        fiat_balance = self._fiat_balance
        available_fiat = self._available_fiat_balance
        crypto_balance = self._crypto_balance
        available_crypto = self._available_crypto_balance

        return (f"Balance(fiat_balance={fiat_balance:.2f}, "
                f"available_fiat_balance={available_fiat:.2f}, "
                f"crypto_balance={crypto_balance:.2f}, "
                f"available_crypto_balance={available_crypto:.2f})")


class BalanceInfo(AbstractBalance):
    """
    Wrapper around `Balance` that provides a read-only view
    into the wrapped `Balance` data.
    """
    def __init__(self, data: Balance):
        self._data = data

    @property
    def available_fiat_balance(self) -> Decimal:
        """Get fiat available for trading."""
        return self._data.available_fiat_balance

    @property
    def available_crypto_balance(self) -> Decimal:
        """Get crypto available for trading."""
        return self._data.available_crypto_balance

    @property
    def fiat_balance(self) -> Decimal:
        """Get fiat balance."""
        return self._data.fiat_balance

    @property
    def crypto_balance(self) -> Decimal:
        """Get crypto balance."""
        return self._data.crypto_balance

    def __repr__(self) -> str:
        fiat_balance = self.fiat_balance
        available_fiat = self.available_fiat_balance
        crypto_balance = self.crypto_balance
        available_crypto = self.available_crypto_balance

        return (f"BalanceInfo(fiat_balance={fiat_balance:.2f}, "
                f"available_fiat_balance={available_fiat:.2f}, "
                f"crypto_balance={crypto_balance:.2f}, "
                f"available_crypto_balance={available_crypto:.2f})")