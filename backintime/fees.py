from dataclasses import dataclass


@dataclass
class Fees:
    maker_fee: float
    taker_fee: float

    def __call__(self, price, taker=True) -> float:
        fee = self.taker_fee if taker else self.maker_fee
        return price*fee
