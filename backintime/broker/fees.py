from decimal import Decimal   # https://docs.python.org/3/library/decimal.html


class FeesEstimator:
    def __init__(self, maker_fee: Decimal, taker_fee: Decimal):
        self._maker_fee = self._validate_fee(maker_fee)
        self._taker_fee = self._validate_fee(taker_fee)

    @property
    def maker_fee(self) -> Decimal:
        """Get maker fee."""
        return self._maker_fee

    @property 
    def taker_fee(self) -> Decimal:
        """Get taker fee."""
        return self._taker_fee

    def estimate_maker_price(self, price: Decimal) -> Decimal:
        """
        Estimate price including maker fee. 
        Only makes sence for BUY orders.
        """
        return price * (1 + self._maker_fee)

    def estimate_taker_price(self, price: Decimal) -> Decimal:
        """
        Estimate price including taker fee.
        Only makes sence for BUY orders.
        """
        return price * (1 + self._taker_fee)

    def estimate_taker_gain(self, price: Decimal) -> Decimal:
        """
        Estimate gain minus taker fee. 
        Only makes sence for SELL orders.
        """
        return price * (1 - self._taker_fee)

    def estimate_maker_gain(self, price: Decimal) -> Decimal:
        """
        Estimate gain minus maker fee.
        Only makes sence for SELL orders.
        """
        return price * (1 - self._maker_fee)

    def _validate_fee(self, fee: Decimal) -> Decimal:
        """Validate fee."""
        if not fee >= 0 and fee < 1:
            raise ValueError("fee rates must be in [0, 1)")
        return fee
