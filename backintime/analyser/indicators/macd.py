import ta
import numpy
import pandas as pd
import typing as t
from dataclasses import dataclass
from backintime.timeframes import Timeframes
from .constants import CLOSE
from .base import MarketData, IndicatorParam, IndicatorResultSequence


@dataclass
class MacdResultItem:
    macd: numpy.float64
    signal: numpy.float64
    hist: numpy.float64


class MacdResultSequence(IndicatorResultSequence[MacdResultItem]):
    def __init__(self,
                 macd: numpy.ndarray,
                 signal: numpy.ndarray,
                 hist: numpy.ndarray):
        self.macd = macd
        self.signal = signal
        self.hist = hist

    def crossover_up(self) -> bool:
        return self.hist[-1] > 0 and self.hist[-2] <= 0

    def crossover_down(self) -> bool:
        return self.hist[-1] <= 0 and self.hist[-2] > 0

    def __iter__(self) -> t.Iterator[MacdResultItem]:
        zip_iter = zip(self.macd, self.signal, self.hist)
        return (
            MacdResultItem(macd, signal, hist) 
                for macd, signal, hist in zip_iter
        )

    def __reversed__(self) -> t.Iterator[MacdResultItem]:
        reversed_iter = zip(reversed(self.macd), 
                            reversed(self.signal), 
                            reversed(self.hist))
        return (
            MacdResultItem(macd, signal, hist) 
                for macd, signal, hist in reversed_iter
        )

    def __getitem__(self, index: int) -> MacdResultItem:
        return MacdResultItem(self.macd[index], 
                              self.signal[index], 
                              self.hist[index])

    def __len__(self) -> int:
        return min(len(self.macd), len(self.signal), len(self.hist))

    def __repr__(self) -> str:
        return (f"MacdResultSequence(macd={self.macd}, "
                f"signal={self.signal}, hist={self.hist})")


def macd(market_data: MarketData, 
         timeframe: Timeframes,
         fastperiod: int = 12,
         slowperiod: int = 26,
         signalperiod: int = 9) -> MacdResultSequence:
    """
    Moving Average Convergence Divergence (MACD).

    Trend-following momentum indicator that shows the 
    relationship between two moving averages of prices.
    """
    quantity = slowperiod * signalperiod
    close = market_data.get_values(timeframe, CLOSE, quantity)
    close = pd.Series(close)
    macd = ta.trend.MACD(close, slowperiod, fastperiod, signalperiod)

    return MacdResultSequence(macd.macd().values,
                              macd.macd_signal().values,
                              macd.macd_diff().values)


def macd_params(timeframe: Timeframes,
                fastperiod: int = 12,
                slowperiod: int = 26,
                signalperiod: int = 9) -> t.Tuple[IndicatorParam]:
    """Get list of MACD params."""
    return (
        IndicatorParam(timeframe=timeframe, 
                       candle_property=CLOSE,
                       quantity=slowperiod * signalperiod),
    )