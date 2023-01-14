import numpy
import typing as t
import pandas as pd
from enum import Enum
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import HIGH, LOW, CLOSE
from .base import (
    MarketData,
    BaseIndicator, 
    IndicatorParam,
    IndicatorFactory,
    IndicatorResultSequence
)


@dataclass
class TraditionalPivotPointsItem:
    pivot:  numpy.float64
    s1:     numpy.float64
    s2:     numpy.float64
    s3:     numpy.float64
    s4:     numpy.float64
    s5:     numpy.float64
    r1:     numpy.float64
    r2:     numpy.float64
    r3:     numpy.float64
    r4:     numpy.float64
    r5:     numpy.float64


@dataclass
class ClassicPivotPointsItem:
    pivot:  numpy.float64
    s1:     numpy.float64
    s2:     numpy.float64
    s3:     numpy.float64
    s4:     numpy.float64
    r1:     numpy.float64
    r2:     numpy.float64
    r3:     numpy.float64
    r4:     numpy.float64


@dataclass
class FibonacciPivotPointsItem:
    pivot:  numpy.float64
    s1:     numpy.float64
    s2:     numpy.float64
    s3:     numpy.float64
    r1:     numpy.float64
    r2:     numpy.float64
    r3:     numpy.float64


class PivotPointsTypes(Enum):
    TRADITIONAL_PIVOT = "TRADITIONAL"
    CLASSIC_PIVOT = "CLASSIC"
    FIBONACCI_PIVOT = "FIBONACCI"


TRADITIONAL_PIVOT = PivotPointsTypes.TRADITIONAL_PIVOT
CLASSIC_PIVOT = PivotPointsTypes.CLASSIC_PIVOT
FIBONACCI_PIVOT = PivotPointsTypes.FIBONACCI_PIVOT


class UnexpectedPivotPointsType(Exception):
    def __init__(self, 
                 pivot_type: t.Any, 
                 supported: t.Iterable[PivotPointsTypes]):
        message = (f"Unexpected pivot points type `{pivot_type}`. "
                   f"Supported types are: {supported}.")
        super().__init__(message)


class TraditionalPivotPoints(IndicatorResultSequence[TraditionalPivotPointsItem]):
    def __init__(self, 
                 pivot,
                 s1: numpy.ndarray,
                 s2: numpy.ndarray,
                 s3: numpy.ndarray,
                 s4: numpy.ndarray,
                 s5: numpy.ndarray,
                 r1: numpy.ndarray,
                 r2: numpy.ndarray,
                 r3: numpy.ndarray,
                 r4: numpy.ndarray,
                 r5: numpy.ndarray):
        self.pivot = pivot
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.s5 = s5
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.r5 = r5

    def __iter__(self) -> t.Iterator[TraditionalPivotPointsItem]:
        zip_iter = zip(self.pivot, 
                       self.s1, self.s2, self.s3, self.s4, self.s5, 
                       self.r1, self.r2, self.r3, self.r4, self.r5)
        return (
            TraditionalPivotPointsItem(*values) 
                for values in zip_iter
        )

    def __reversed__(self) -> t.Iterator[TraditionalPivotPointsItem]:
        reversed_iter = zip(reversed(self.pivot), 
                            reversed(self.s1), 
                            reversed(self.s2), reversed(self.s3), 
                            reversed(self.s4), reversed(self.s5),
                            reversed(self.r1), reversed(self.r2), 
                            reversed(self.r3), reversed(self.r4), 
                            reversed(self.r5))
        return (
            TraditionalPivotPointsItem(*values) 
                for values in reversed_iter
        )

    def __getitem__(self, index: int) -> TraditionalPivotPointsItem:
        return TraditionalPivotPointsItem(self.pivot[index],
                                          self.s1[index], 
                                          self.s2[index], self.s3[index], 
                                          self.s4[index], self.s5[index],
                                          self.r1[index], self.r2[index], 
                                          self.r3[index], self.r4[index],
                                          self.r5[index])

    def __repr__(self) -> str:
        return (f"TraditionalPivotPoints(pivot={self.pivot}, "
                f"s1={self.s1}, s2={self.s2}, "
                f"s3={self.s3}, s4={self.s4}, s5={self.s5}, "
                f"r1={self.r1}, r2={self.r2}, "
                f"r3={self.r3}, r4={self.r4}, r5={self.r5})")


class ClassicPivotPoints(IndicatorResultSequence[ClassicPivotPointsItem]):
    def __init__(self, 
                 pivot,
                 s1: numpy.ndarray,
                 s2: numpy.ndarray,
                 s3: numpy.ndarray,
                 s4: numpy.ndarray,
                 r1: numpy.ndarray,
                 r2: numpy.ndarray,
                 r3: numpy.ndarray,
                 r4: numpy.ndarray):
        self.pivot = pivot
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4

    def __iter__(self) -> t.Iterator[ClassicPivotPointsItem]:
        zip_iter = zip(self.pivot, 
                       self.s1, self.s2, self.s3, self.s4, 
                       self.r1, self.r2, self.r3, self.r4)
        return (
            ClassicPivotPointsItem(*values) 
                for values in zip_iter
        )

    def __reversed__(self) -> t.Iterator[ClassicPivotPointsItem]:
        reversed_iter = zip(reversed(self.pivot), 
                            reversed(self.s1), reversed(self.s2), 
                            reversed(self.s3), reversed(self.s4), 
                            reversed(self.r1), reversed(self.r2), 
                            reversed(self.r3), reversed(self.r4))
        return (
            ClassicPivotPointsItem(*values) 
                for values in reversed_iter
        )

    def __getitem__(self, index: int) -> ClassicPivotPointsItem:
        return ClassicPivotPointsItem(self.pivot[index],
                                      self.s1[index], self.s2[index], 
                                      self.s3[index], self.s4[index], 
                                      self.r1[index], self.r2[index], 
                                      self.r3[index], self.r4[index])

    def __repr__(self) -> str:
        return (f"ClassicPivotPoints(pivot={self.pivot}, "
                f"s1={self.s1}, s2={self.s2}, "
                f"s3={self.s3}, s4={self.s4}, "
                f"r1={self.r1}, r2={self.r2}, "
                f"r3={self.r3}, r4={self.r4})")


class FibonacciPivotPoints(IndicatorResultSequence[FibonacciPivotPointsItem]):
    def __init__(self, 
                 pivot,
                 s1: numpy.ndarray,
                 s2: numpy.ndarray,
                 s3: numpy.ndarray,
                 r1: numpy.ndarray,
                 r2: numpy.ndarray,
                 r3: numpy.ndarray):
        self.pivot = pivot
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3

    def __iter__(self) -> t.Iterator[FibonacciPivotPointsItem]:
        zip_iter = zip(self.pivot, 
                       self.s1, self.s2, self.s3, 
                       self.r1, self.r2, self.r3)
        return (
            FibonacciPivotPointsItem(*values) 
                for values in zip_iter
        )

    def __reversed__(self) -> t.Iterator[FibonacciPivotPointsItem]:
        reversed_iter = zip(reversed(self.pivot), 
                            reversed(self.s1), reversed(self.s2), 
                            reversed(self.s3), 
                            reversed(self.r1), reversed(self.r2), 
                            reversed(self.r3))
        return (
            FibonacciPivotPointsItem(*values) 
                for values in reversed_iter
        )

    def __getitem__(self, index: int) -> FibonacciPivotPointsItem:
        return FibonacciPivotPointsItem(self.pivot[index],
                                        self.s1[index], self.s2[index], 
                                        self.s3[index], 
                                        self.r1[index], self.r2[index], 
                                        self.r3[index])

    def __repr__(self) -> str:
        return (f"FibonacciPivotPoints(pivot={self.pivot}, "
                f"s1={self.s1}, s2={self.s2}, s3={self.s3}, "
                f"r1={self.r1}, r2={self.r2}, r3={self.r3})"


PivotPointsSequence = t.TypeVar('PivotPointsSequence',
                                bound=t.Union[TraditionalPivotPoints,
                                              ClassicPivotPoints,
                                              FibonacciPivotPoints])


def typical_price(highs: pd.Series, lows: pd.Series, 
                        close: pd.Series) -> pd.Series:
    return (highs + lows + close) / 3


class PivotPoints(BaseIndicator):
    def __init__(self, 
                 market_data: MarketData,
                 timeframe: Timeframes,
                 period: int,
                 pivot_type: PivotPointsTypes):
        self._timeframe = timeframe
        self._period = period
        self._quantity = period + 1
        self._pivot_type = pivot_type
        super().__init__(market_data)

    def __call__(self) -> PivotPointsSequence:
        market_data = self.market_data
        timeframe = self._timeframe
        qty = self._quantity

        highs = market_data.get_values(timeframe, HIGH, qty)
        highs = highs[:-1]   # or 1:?
        highs = pd.Series(highs, dtype=numpy.float64)

        lows = market_data.get_values(timeframe, LOW, qty)
        lows = lows[:-1]
        lows = pd.Series(lows, dtype=numpy.float64)

        close = market_data.get_values(timeframe, CLOSE, qty)
        close = close[:-1]
        close = pd.Series(close, dtype=numpy.float64)
        
        if self._pivot_type is TRADITIONAL_PIVOT:
            return self._traditional_pivot_points(highs, lows, close)
        elif self._pivot_type is CLASSIC_PIVOT:
            return self._classic_pivot_points(highs, lows, close)
        elif self._pivot_type is FIBONACCI_PIVOT:
            return self._fibonacci_pivot_points(highs, lows, close)
        else:
            supported = (TRADITIONAL_PIVOT, CLASSIC_PIVOT, FIBONACCI_PIVOT)
            raise UnexpectedPivotPointsType(self._pivot_type, 
                                            supported)

    def _traditional_pivot_points(
                self, 
                highs: pd.Series, 
                lows: pd.Series, 
                close: pd.Series) -> TraditionalPivotPoints:
        pivot = typical_price(highs, lows, close)  
        # TRADITIONAL
        s1 = (pivot * 2) - highs
        s2 = pivot - (highs - lows)
        s3 = lows - (2 * (highs - pivot))
        s4 = lows - (3 * (highs - pivot))
        s5 = lows - (4 * (highs - pivot))

        r1 = (pivot * 2) - lows
        r2 = pivot + (highs - lows)
        r3 = highs + (2 * (pivot - lows))
        r4 = highs + (3 * (pivot - lows))
        r5 = highs + (4 * (pivot - lows))

        return TraditionalPivotPoints(pivot.values, 
                                      s1.values, s2.values, s3.values,
                                      s4.values, s5.values, 
                                      r1.values, r2.values, r3.values, 
                                      r4.values, r5.values)

    def _classic_pivot_points(self, 
                              highs: pd.Series, 
                              lows: pd.Series, 
                              close: pd.Series) -> ClassicPivotPoints: 
        pivot = typical_price(highs, lows, close)        
        # CLASSIC
        s1 = (pivot * 2) - highs
        s2 = pivot - (highs - lows)
        s3 = pivot - 2 * (highs - lows)
        s4 = pivot - 3 * (highs - lows)

        r1 = (pivot * 2) - lows
        r2 = pivot + (highs - lows)
        r3 = pivot + 2 * (highs - lows)
        r4 = pivot + 3 * (highs - lows)

        return ClassicPivotPoints(pivot.values, 
                                  s1.values, s2.values, 
                                  s3.values, s4.values, 
                                  r1.values, r2.values, 
                                  r3.values, r4.values)

    def _fibonacci_pivot_points(self, 
                                highs: pd.Series, 
                                lows: pd.Series, 
                                close: pd.Series) -> FibonacciPivotPoints:
        pivot = typical_price(highs, lows, close)
        # FIBONACCI
        s1 = pivot - 0.382 * (highs - lows)
        s2 = pivot - 0.618 * (highs - lows)
        s3 = pivot - (highs - lows)

        r1 = pivot + 0.382 * (highs - lows)
        r2 = pivot + 0.618 * (highs - lows)
        r3 = pivot + (highs - lows)

        return FibonacciPivotPoints(pivot.values, 
                                    s1.values, s2.values, s3.values,
                                    r1.values, r2.values, r3.values)


class PivotPointsFactory(IndicatorFactory):
    def __init__(self, 
                 timeframe: Timeframes,
                 period: int = 15,
                 pivot_type: PivotPointsTypes = TRADITIONAL_PIVOT,
                 name: str = ''):
        self.timeframe = timeframe
        self.period = period
        self.pivot_type = pivot_type
        self._name = name or f"pivot_{str.lower(timeframe.name)}"

    @property
    def indicator_name(self) -> str:
        return self._name

    @property
    def indicator_params(self) -> t.Sequence[IndicatorParam]:
        return [
            IndicatorParam(self.timeframe, HIGH, self.period + 1),
            IndicatorParam(self.timeframe, LOW, self.period + 1),
            IndicatorParam(self.timeframe, CLOSE, self.period + 1)
        ]

    def create(self, market_data: MarketData) -> PivotPoints:
        return PivotPoints(market_data, self.timeframe, 
                           self.period, self.pivot_type)