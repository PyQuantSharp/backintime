import heapq
from enum import Enum
from dataclasses import dataclass, asdict
import datetime

OrderTypes=Enum('OrderTypes', 'Market Limit')
OrderStatus=Enum('OrderStatus', 'Created Submitted Cancelled Executed')


class TradeAccount:
    def __init__(self, start_money):
        self._base_currency_balance=start_money
        self._trade_currency_balance=10
        self._trades = []

    def base_currency_balance(self):
        return self._base_currency_balance

    def trade_currency_balance(self):
        return self._trade_currency_balance

    def lock(self, amount=None, base_currency=True):
        if base_currency:
            if not amount:
                amount = self._base_currency_balance
            self._base_currency_balance -= amount
        else:
            if not amount:
                amount = self._trade_currency_balance
            self._trade_currency_balance -= amount
        return amount

    def unlock(self, amount, base_currency=True):
        self.mod_balance(amount, base_currency)

    def mod_balance(self, quantity, base_currency=True):
        if base_currency:
            self._base_currency_balance += quantity
        else:
            self._trade_currency_balance += quantity

    def add_trade(self, trade):
        self._trades.append(trade)

    def trades(self):
        return (x for x in self._trades)

    def __repr__(self):
        return f'<TradeAccount> ( {self._base_currency_balance} {self._trade_currency_balance} )'

class Order:
    def __init__(self, type_, side, price=None, quantity=None):
        self.type=type_
        self.side=side
        self.price=price
        self.quantity=quantity
        self.pledge=0
        self._status=OrderStatus.Created
        self.notional=0

    def __repr__(self):
        return f'<Order> ({self.type}, {self.side}, {self.notional}, {self.price}, {self.quantity}, {self.pledge}, {self._status})'

class OrdersRepository:
    '''
    Use priority queue for limit orders,
    and list/queue for market ones
    '''
    def __init__(self):
        # map order to item in priority queue
        self._entry_finder = {}
        self._orders = {
            OrderTypes.Market: [],
            OrderTypes.Limit: []
        }

    def append(self, order):
        order_t = order.type
        collection = self._orders[order_t]

        if order_t is OrderTypes.Limit:
            entry = (order.price, order)
            self._entry_finder[order] = entry
            heapq.heappush(collection, entry)
        else:
            self._orders[order_t].append(order)

    def remove(self, order):
        order_t = order.type
        collection = self._orders[order_t]
        entry = order
        if order_t is OrderTypes.Limit:
            entry = self._entry_finder[order]
        collection.remove(entry)

    def items(self):
        return self._orders.items()

    def __len__(self):
        return sum(lambda orders: len(orders), self._orders.values())

@dataclass
class Candle:
    open: float = None
    high: float = None
    low: float  = None
    close: float= None
    time: None  = None

@dataclass
class Trade:
    order: Order
    profit: float
    time_1: datetime.datetime=None
    time_2: datetime.datetime=None

class CandlesProvider:
    def __init__(self):
        self._candle_buf = Candle()

    def current_candle(self):
        return self._candle_buf

    def update(self):
        self._candle_buf.open = 6000
        self._candle_buf.high = 7000
        self._candle_buf.low = 5500
        self._candle_buf.close = 6600
        self._candle_buf.time = None

class Broker:

    _taker_fee = 0.001
    _maker_fee = 0.001

    def __init__(self, market_data: CandlesProvider, start_money: float):
        self._account = TradeAccount(start_money)
        self._market_data = market_data
        self._orders = OrdersRepository()

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

    def _execute(self, order, price, time):
        # закинуть валюту на баланс
        # удалить из коллекции ордеров
        # за выполнение ордера берется комиссия
        profit = 0

        if order.side == 'BUY':
            if not order.pledge:
                # залога не было
                price = order.notional
                fee = self._fee(price, order.type==OrderTypes.Market)
                price = price + fee

                if price >= self._account.base_currency_balance():
                    self.cancel(order)
                    return
                profit = - price
                self._account.mod_balance(profit)
            else:
                profit = - order.pledge
            self._account.mod_balance(order.quantity, False)

        elif order.side == 'SELL':
            # profit without fee
            profit = order.notional
            # profit minus fee
            fee = self._fee(profit, order.type==OrderTypes.Market)
            profit = profit - fee
            self._account.mod_balance(profit)

        print(f'deal profit: {profit}')
        print(f'deal time_1: {time}')
        trade = Trade(order, profit)
        self._account.add_trade(trade)
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

    @classmethod
    def _fee(cls, price, taker=True):
        fee = cls._taker_fee if taker else cls._maker_fee
        return price*fee

    def update(self):
        candle = self._market_data.current_candle()
        for order_t, orders in self._orders.items():
            if order_t == OrderTypes.Market:
                # закрыть все по цене открытия
                for order in orders:
                    # "вот все деньги, возьми на сколько хватит"
                    if not order.quantity:
                        order.quantity = order.notional / candle.open
                    if not order.notional:
                        order.notional = order.quantity*candle.open
                    self._execute(order, candle.open, candle.time)

            elif order_t == OrderTypes.Limit:
                for order in orders:
                    order = order[1]
                    if (price := self._match_price(order, candle)):
                        self._execute(order, price, candle.time)


market_data = CandlesProvider()
broker = Broker(market_data, 25000)
print(broker._account)
order = Order(OrderTypes.Limit, 'SELL', 6000)
broker.submit(order)
print(order)
print(broker._account)

market_data.update()
broker.update()
print(order)
print(broker._account)

trade = list(broker._account.trades())[0]
print(asdict(trade))
