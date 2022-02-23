from enum import Enum

from .trade import Trade
from ..exceptions import UnsufficientFunds


OrderStatus=Enum('OrderStatus', 'Created Submitted Cancelled Executed')
OrderTypes=Enum('OrderTypes', 'Market Limit')


class Order:
    def __init__(self, order_type: OrderTypes, price=None, quantity=None):
        self.type=order_type
        self.price=price
        self.quantity=quantity
        self.pledge=None    # сколько денег мы сняли с аккаунта для обесп. ордера
        self.notional=None  # реальная стоимость ордера
        self._account=None  # reserved to be completed by broker later
        self._fee = None    # reserved to be completed by broker later
        self._status=OrderStatus.Created

    def __repr__(self):
        return (
            f'<Order> ({self.notional}, {self.price},'
            f'{self.quantity}, {self.pledge}, {self._status})')


class MarketOrder(Order):
    def update(self, candle):
        time_1 = candle.open_time

        if not self.quantity:
            self.quantity = self.notional / candle.open
        if not self.notional:
            self.notional = self.quantity*candle.open
        trade = self._execute(candle.open, time_1, time_1)
        return trade


class LimitOrder(Order):
    def __init__(self, price=None, quantity=None):
        super().__init__(OrderTypes.Limit, price, quantity)

    def _match_price(self, candle):
        if self.price >= candle.low and self.price <= candle.high:
            return self.price
        else:
            return None

    def update(self, candle):
        time_1 = candle.open_time

        if (price := self._match_price(order, candle)):
            time_2 = candle.close_time
            trade = self._execute(order, price, time_1, time_2)
            return trade

class BuyOrder(Order):
    def _execute(self, price, time_1, time_2):
        fee = self.pledge - self.notional
        profit = - self.pledge
        self.price = price  # ?
        self._account.mod_balance(self.quantity, False)
        return Trade(time_1, time_2, self, profit, fee)


class MarketBuy(MarketOrder, BuyOrder):

    def __init__(self, quantity=None):
        super().__init__(OrderTypes.Market, None, quantity)

    def _execute(self, price, time_1, time_2):
        if not self.pledge:
            price = self.notional
            fee = self._fee(price)
            price += fee

            if price >= self._account.base_currency_balance():
                raise UnsufficientFunds()
            profit = - price
            self._account.mod_balance(profit)
        else:
            fee = self.pledge - self.notional
            profit = - self.pledge
        self.price = price
        self._account.mod_balance(self.quantity, False)
        return Trade(time_1, time_2, self, profit, fee)


    def _lock_funds(self):
        if not self.quantity:
            self.pledge = self._account.lock()
            fee = self._fee(self.pledge)
            # закладываем комиссю в notional = сможем купить чуть меньше
            self.notional = self.pledge - fee


class LimitBuy(LimitOrder, BuyOrder):
    def _lock_funds(self):
        if self.quantity:
            self.notional = self.price*self.quantity
            fee = self._fee(self.notional, False)
            total_price = self.notional + fee
            # снимаем деньги с комиссией. А ордер и так сформирован
            self.pledge = self._account.lock(total_price)
        else:
            self.pledge = self._account.lock()
            fee = self._fee(self.pledge, False)
            # закладываем комиссю в notional = сможем купить чуть меньше
            self.notional = self.pledge - fee
            self.quantity = self.notional / self.price


class SellOrder(Order):
    def _execute(self, price, time_1, time_2):
        # profit without fee
        profit = self.notional
        # profit minus fee
        fee = self._fee(profit, self.type==OrderTypes.Market)
        profit -= fee
        self._account.mod_balance(profit)
        return Trade(time_1, time_2, self, profit, fee)

    def _lock_funds(self):
        self.pledge = self._account.lock(self.quantity, base_currency=False)
        self.quantity = self.pledge
        

class MarketSell(MarketOrder, SellOrder):
    def __init__(self, quantity=None):
        super().__init__(OrderTypes.Market, None, quantity)

    def _execute(self, price, time_1, time_2):
        if not self.price:
            self.price = self
        return super()._execute(price, time_1, time_2)


class LimitSell(LimitOrder, SellOrder):
    def _lock_funds(self):
        # все как у селл
        super()._lock_funds()
        self.notional = self.price*self.quantity
