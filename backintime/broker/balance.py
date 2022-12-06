import typing as t
from decimal import Decimal   # https://docs.python.org/3/library/decimal.html


class InsufficientFunds(Exception):
    def __init__(self):
        super().__init__("Insufficient funds")


class Balance:
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
        fiat_balance = round(self._fiat_balance, 2)
        available_fiat_balance = round(self._available_fiat_balance, 2)
        crypto_balance = round(self._crypto_balance, 2)
        available_crypto_balance = round(self._available_crypto_balance, 2)

        return (f"Balance(fiat_balance={fiat_balance}, "
                f"available_fiat_balance={available_fiat_balance}, "
                f"crypto_balance={crypto_balance}, "
                f"available_crypto_balance={available_crypto_balance})")
