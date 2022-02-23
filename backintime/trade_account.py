from .exceptions import UnsufficientFunds
from .broker.position import Position


class TradeAccount:
    """
    holds info about account
    like current balance and trades history
    """
    def __init__(self, start_money):
        self._base_currency_balance=start_money
        self._trade_currency_balance=0
        self._positions = []

    def base_currency_balance(self):
        return self._base_currency_balance

    def trade_currency_balance(self):
        return self._trade_currency_balance

    def lock(self, quantity=None, base_currency=True):
        if quantity and quantity <= 0:
            return
        if base_currency:
            if not quantity:
                quantity = self._base_currency_balance
            elif quantity > self._base_currency_balance:
                raise UnsufficientFunds()
            self._base_currency_balance -= quantity
        else:
            if not quantity:
                quantity = self._trade_currency_balance
            elif quantity > self._trade_currency_balance:
                raise UnsufficientFunds()
            self._trade_currency_balance -= quantity
        return quantity

    def unlock(self, quantity, base_currency=True):
        if quantity > 0:
            self.mod_balance(quantity, base_currency)

    def mod_balance(self, quantity, base_currency=True):
        if base_currency:
            self._base_currency_balance += quantity
        else:
            self._trade_currency_balance += quantity

    def add_position(self, position: Position) -> None:
        self._positions.append(position)

    def positions(self):
        # list of trades I suppose
        return self._positions

    def __repr__(self):
        return (
            f'<TradeAccount> (',
            'base currency: {self._base_currency_balance} ',
            'trade currency: {self._trade_currency_balance} )')
