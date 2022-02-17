from collections import namedtuple

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import talib


class BBANDS(Oscillator):

    Result = namedtuple('Result', 'upperband middleband lowerband')

    def __init__(
            self,
            timeframe: Timeframes,
            period: int,
            property: CandleProperties=CandleProperties.CLOSE,
            deviation_quotient: int=2,
            name: str=None
            ):

        if not name:
            if property != CandleProperties.CLOSE:
                name = f'BBANDS_{timeframe.name}_{period}_{property.name}'
            else:
                name = f'BBANDS_{timeframe.name}_{period}'

        self._timeframe = timeframe
        self._property = property
        self._period = period
        self._devq = deviation_quotient
        #
        self._reserved_size = 300
        super().__init__(name)

    def reserve(self) -> None:
        self._market_data.reserve(
            self._timeframe,
            self._property,
            self._reserved_size
        )

    def __call__(self) -> Result:
        values = self._market_data.get(
            self._timeframe,
            self._property,
            self._reserved_size
        )

        upperband, middleband, lowerband = talib.BBANDS(
            values,
            self._period,
            nbdevup=self._devq,
            nbdevdn=self._devq
        )

        return BBANDS.Result(upperband[-1], middleband[-1], lowerband[-1])
