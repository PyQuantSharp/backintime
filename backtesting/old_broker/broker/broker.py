from ..candles_providers import CandlesProvider
from ..fees import Fees
from ..trade_account import TradeAccount
from ..trade_account.trade import Trade
from .orders_repository import OrdersRepository
from .order import Order, OrderTypes, OrderStatus
from .position import Position


class Broker:

    def __init__(self, market_data: CandlesProvider, start_money: float, fees: Fees):
        self._account = TradeAccount(start_money)
        self._market_data = market_data
        self._fee = fees
        self._orders = OrdersRepository()
        self._position = Position(self._account)

    def has_orders(self) -> bool:
        return bool(len(self._orders))

    def submit(self, order):
        # добавить обеспечение ордеру, если нужно
        # добавить ордер в коллекцию ордеров
        self._lock_funds(order)
        self._orders.append(order)
        order._status = OrderStatus.Submitted

    def cancel(self, order):
        # снять обеспечение ордера, если нужно
        # удалить из коллекции ордеров
        self._unlock_funds(order)
        self._orders.remove(order)
        order._status = OrderStatus.Cancelled

    def _execute(self, order, price, time_1, time_2):
        # закинуть валюту на баланс
        # удалить из коллекции ордеров
        # за выполнение ордера берется комиссия
        profit = 0

        if order.side == 'BUY':
            if not order.pledge:
                # залога не было
                price = order.notional
                fee = self._fee(price, order.type==OrderTypes.Market)
                price += fee

                if price >= self._account.base_currency_balance():
                    self.cancel(order)
                    return
                profit = - price
                self._account.mod_balance(profit)
            else:
                fee = order.pledge - order.notional
                profit = - order.pledge
            order.price = price
            self._account.mod_balance(order.quantity, False)

        elif order.side == 'SELL':
            # profit without fee
            profit = order.notional
            # profit minus fee
            fee = self._fee(profit, order.type==OrderTypes.Market)
            profit -= fee
            # market sell only
            if not order.price:
                order.price = price
            # end
            self._account.mod_balance(profit)

        trade = Trade(time_1, time_2, order, profit, fee)
        self._position.add_trade(trade)
        if self._position.closed():
            self._account.add_position(self._position)
            self._position = Position(self._account)

        self._orders.remove(order)
        order._status = OrderStatus.Executed

    def _lock_funds(self, order):

        if order.side == 'BUY':
            # короче при execute с BUY комиссию не берём
            # ее уже взяли с виде лока. А при execute мы лок не снимаем, так что в расчете
            if order.type == OrderTypes.Limit:
                if order.quantity:
                    order.notional = order.price*order.quantity
                    fee = self._fee(order.notional, False)
                    total_price = order.notional + fee
                    # снимаем деньги с комиссией. А ордер и так сформирован
                    order.pledge = self._account.lock(total_price)
                else:
                    order.pledge = self._account.lock()
                    fee = self._fee(order.pledge, False)
                    # закладываем комиссю в notional = сможем купить чуть меньше
                    order.notional = order.pledge - fee
                    order.quantity = order.notional / order.price
            # Market
            else:
                if not order.quantity:
                    order.pledge = self._account.lock()
                    fee = self._fee(order.pledge)
                    # закладываем комиссю в notional = сможем купить чуть меньше
                    order.notional = order.pledge - fee

        # SELL = берем комиссию при execute с прибыли
        elif order.side == 'SELL':
            # снимаем с аккаунта ровно столько, сколько хотим продать
            # указанное количество попадает на биржу
            order.pledge = self._account.lock(order.quantity, base_currency=False)
            order.quantity = order.pledge
            if order.type == OrderTypes.Limit:
                order.notional = order.price*order.quantity

    def _unlock_funds(self, order):
        if order.pledge:
            self._account.unlock(order.pledge, base_currency=order.side=='BUY')

    @staticmethod
    def _match_price(order, candle):
        if order.price >= candle.low and order.price <= candle.high:
            return order.price
        else:
            return None

    def positions(self):
        return self._account.positions()

    def position(self):
        return self._position

    def update(self):
        candle = self._market_data.current_candle()
        time_1 = candle.open_time

        for order_t, orders in self._orders.items():
            if order_t == OrderTypes.Market:
                # закрыть все по цене открытия
                for order in orders:
                    # "вот все деньги, возьми на сколько хватит"
                    if not order.quantity:
                        order.quantity = order.notional / candle.open
                    if not order.notional:
                        order.notional = order.quantity*candle.open
                    self._execute(order, candle.open, time_1, time_1)

            elif order_t == OrderTypes.Limit:
                for order in orders:
                    order = order[1]
                    if (price := self._match_price(order, candle)):
                        time_2 = candle.close_time
                        self._execute(order, price, time_1, time_2)
