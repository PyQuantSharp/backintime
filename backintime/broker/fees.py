

class FeesEstimator:
    def __init__(self, maker_fee: float, taker_fee: float):
        self._maker_fee = self._validate_fee(maker_fee)
        self._taker_fee = self._validate_fee(taker_fee)

    @property
    def maker_fee(self) -> float:
        """Get maker fee."""
        return self._maker_fee

    @property 
    def taker_fee(self) -> float:
        """Get taker fee."""
        return self._taker_fee

    def estimate_maker_price(self, price: float) -> float:
        """
        Estimate price including maker fee. 
        Only makes sence for BUY orders.
        """
        return price * (1 + self._maker_fee)

    def estimate_taker_price(self, price: float) -> float:
        """
        Estimate price including taker fee.
        Only makes sence for BUY orders.
        """
        return price * (1 + self._taker_fee)

    def estimate_taker_gain(self, price: float) -> float:
        """
        Estimate gain minus taker fee. 
        Only makes sence for SELL orders.
        """
        return price * (1 - self._taker_fee)

    def estimate_maker_gain(self, price: float) -> float:
        """
        Estimate gain minus maker fee.
        Only makes sence for SELL orders.
        """
        return price * (1 - self._maker_fee)

    def _validate_fee(self, fee: float) -> float:
        """Validate fee."""
        if not fee >= 0 and fee < 1:
            raise ValueError("fee rates must be in [0, 1)")
        return fee
