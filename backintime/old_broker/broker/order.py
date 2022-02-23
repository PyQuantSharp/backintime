from enum import Enum

OrderTypes=Enum('OrderTypes', 'Market Limit')
OrderStatus=Enum('OrderStatus', 'Created Submitted Cancelled Executed')


class Order:

    def __init__(self, order_type: OrderTypes, side: str, price=None, quantity=None):
        self.type=order_type
        self.side=side
        self.price=price
        self.quantity=quantity
        self.pledge=None    # сколько денег мы сняли с аккаунта для обесп. ордера
        self.notional=None  # реальная стоимость ордера
        self._status=OrderStatus.Created

    def __repr__(self):
        return (
            f'<Order> ({self.type}, {self.side}'
            f', {self.notional}, {self.price}, {self.quantity}'
            f', {self.pledge}, {self._status})')
