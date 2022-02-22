from typing import Callable
from collections import namedtuple
from ta.volatility import BollingerBands as BollingerBands

from .oscillator import Oscillator
from ..timeframes import Timeframes
from ..market_data_storage import MarketDataStorage
from ..candle_properties import CandleProperties

import pandas as pd


class BBANDS(Oscillator):

    Result = namedtuple('Result', 'upperband middleband lowerband')

    def __init__(
            self,
            market_data: MarketDataStorage,
            timeframe: Timeframes,
            property: CandleProperties,
            period: int,
            deviation_quotient: int=2,
            name: str=None,
            seq: bool=True
    ):
        if not name:
            if property != CandleProperties.CLOSE:
                name = f'BBANDS_{timeframe.name}_{period}_{property.name}'
            else:
                name = f'BBANDS_{timeframe.name}_{period}'

        self._property = property
        self._period = period
        self._devq = deviation_quotient
        self._reserved_size = 300
        self.seq = seq
        super().__init__(market_data, timeframe, name)

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
            self._reserved_size)

        values = pd.Series(values)
        bbands_ = BollingerBands(values, self._period, self._devq)

        upperband = bbands_.bollinger_hband().values
        middleband = bbands_.bollinger_mavg().values
        lowerband = bbands_.bollinger_lband().values

        if not self.seq:
            upperband = upperband[-1]
            middleband = middleband[-1]
            lowerband = lowerband[-1]

        return BBANDS.Result(
            upperband,
            middleband,
            lowerband
        )
        '''
        return BBANDS.Result(
            bbands_.bollinger_hband().values,     # upperband
            bbands_.bollinger_mavg().values,      # middleband
            bbands_.bollinger_lband().values      # lowerband
        )
        '''

def bbands(
        timeframe: Timeframes,
        property: CandleProperties=CandleProperties.CLOSE,
        period: int=20,
        deviation_quotient: int=2,
        name: str=None,
        seq: bool=True
) -> Callable:
    #
    return lambda market_data: BBANDS(
        market_data,
        timeframe,
        property,
        period,
        deviation_quotient,
        name, seq
    )
