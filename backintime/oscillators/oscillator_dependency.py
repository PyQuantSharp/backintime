from ..timeframes import Timeframes
from ..candle_properties import CandleProperties


class OscillatorDependency:
    """ Specifies input argument of some oscillator """
    def __init__(
            self,
            timeframe: Timeframes,
            ohlcv_property: CandleProperties,
            period: int
    ):
        self.timeframe = timeframe
        self.ohlcv_property = ohlcv_property
        self.period = period
