from .orders import OrderStatus
from .orders_repository import OrdersRepository
from .position import Position
from .trade_account import TradeAccount
from ..exceptions import UnsufficientFunds
from ..fees import Fees
from ..candles_providers import CandlesProvider


class Broker:
    """ Broker deals with orders and fees """
    def __init__(self, market_data: CandlesProvider, start_money: float, fees: Fees):
        self._market_data = market_data
        self._account = TradeAccount(start_money)
        self._orders = OrdersRepository()
        self._fees = fees
        self._position = Position(self._account)

    def submit(self, order):
        """
        Mark order as Submitted which means that it can be closed
        in future
        Also lock funds for a pledge, if order notional could be
        inferred from price and quantity
        """
        order._fee = self._fees
        order._account = self._account
        order._lock_funds()
        order._status = OrderStatus.Submitted
        self._orders.append(order)

    def cancel(self, order):
        """ Cancel orders. Funds will be returned if there was a pledge. """
        order._unlock_funds()
        order._status = OrderStatus.Cancelled
        self._orders.remove(order)

    def _execute(self, order):
        order._status = OrderStatus.Executed
        self._orders.remove(order)

    def has_orders(self):
        return bool(len(self._orders))

    def position(self):
        """ Return current positions """
        return self._position

    def positions(self):
        """ Return all closed positions """
        return self._account.positions()

    def _store_trade(self, trade):
        self._position.add_trade(trade)
        if self._position.closed():
            self._account.add_position(self._position)
            self._position = Position(self._account)

    def update(self):
        """
        Runs each time a new candle closes
        to check if there are orders to close
        """
        candle = self._market_data.current_candle()
        try:
            for order in self._orders.items():
                trade = order.update(candle)
                if trade:
                    self._store_trade(trade)
                    self._execute(order)
        except Exception as e:
            if isinstance(e, UnsufficientFunds):
                self.cancel(order)
            else:
                raise e
