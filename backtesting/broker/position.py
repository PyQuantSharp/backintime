from .orders import BuyOrder, SellOrder


class Position:
    """ Long Position closed when --> продавать нечего :-) """
    def __init__(self, account):
        self.profit = None
        self.profit_ratio = None
        self._is_closed = False
        self._account = account
        self._volume = 0
        self._start_balance = account.base_currency_balance()
        self._trades = []

    def add_trade(self, trade):
        order = trade.order

        if isinstance(order, BuyOrder):
            self._volume += order.quantity
        elif isinstance(order, SellOrder):
            self._volume -= order.quantity

        print(f'volume: {self._volume}')

        if not self._volume:
            self._is_closed = True
            self._calc_profit()
        self._trades.append(trade)

    def _calc_profit(self):
        # profit <- dif (account.balance_i - account.balance_j)
        balance = self._account.base_currency_balance()
        self.profit = balance - self._start_balance
        self.profit_ratio = (balance/self._start_balance)*100 - 100

    def opening_price(self):
        return self._trades[0].order.price

    def trades(self):
        return self._trades

    def opened(self):
        return len(self._trades) and not self._is_closed

    def closed(self):
        return self._is_closed
