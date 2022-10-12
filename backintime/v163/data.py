from __future__ import annotations
import typing as t

import requests as r
from datetime import datetime, timezone
from collections import abc
from abc import abstractmethod
from dataclasses import dataclass
from backintime.v163.timeframes import Timeframes as tf

@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float
    open_time: datetime
    close_time: datetime
    is_closed: t.Optional[bool]=True

class DataProvider(abc.Iterable):
	@abstractmethod
	def __iter__(self) -> t.Iterator[Candle]:
		pass

# Utils
def to_ms(time: datetime) -> int:
    return int(time.timestamp()*1000)

def _parse_time(millis_timestamp: int) -> datetime:
    return datetime.utcfromtimestamp(millis_timestamp/1000)

def parse_candle(candle: list) -> Candle:
    return Candle(open_time=_parse_time(candle[0]),
                  open=float(candle[1]),
                  high=float(candle[2]),
                  low=float(candle[3]),
                  close=float(candle[4]),
                  volume=float(candle[5]),
                  close_time=_parse_time(candle[6]))

# Implementations
class BinanceCandlesIterator(abc.Iterator):
    _url = 'https://api.binance.com/api/v3/klines'
    _intervals = {
        tf.M1: '1m',
        tf.M3: '3m',
        tf.M5: '5m',
        tf.M15: '15m',
        tf.M30: '30m',
        tf.H1: '1h',
        tf.H2: '2h',
        tf.H4: '4h',
        tf.D1: '1d',
        tf.W1: '1w'
    }

    def __init__(self, 
                 ticker: str, 
                 timeframe: tf, 
                 since: datetime, 
                 untill: datetime):
        self._ticker = ticker 
        self._tf = timeframe
        self._start_date = since
        self._end_date = untill
        self._interval = self._intervals[timeframe]
        self._candles = self._get_candles()

    def __iter__(self) -> BinanceCandlesIterator:
        return self

    def __next__(self) -> Candle:
        """ Return one candle at a time """
        candle = next(self._candles)
        return parse_candle(candle)

    def candle_duration(self) -> int:
        return self._tf.value

    def _get_candles(self) -> t.Generator[list, None, None]:
        since = to_ms(self._start_date)
        untill = to_ms(self._end_date)

        max_per_request = 1000
        max_time_step = max_per_request*self.candle_duration()*1000
        params = {
            "symbol": self._ticker,
            "interval": self._interval,
            "startTime": None,
            "endTime": untill,
            "limit": max_per_request
        }

        for start_time in range(since, untill, max_time_step):
            # this requests 1k candles at a time
            params["startTime"] = start_time
            res = r.get(self._url, params)
            res.raise_for_status()
            for item in res.json():
                yield item

class BinanceCandles(DataProvider):
    def __init__(self, 
                 ticker: str, 
                 timeframe: Timeframes, 
                 since: datetime, 
                 untill: t.Optional[datetime]=datetime.now(timezone.utc)):
        self._ticker=ticker
        self._timeframe=timeframe
        self._since=since
        self._untill=untill

    def __iter__(self) -> BinanceCandlesIterator:
        return BinanceCandlesIterator(self._ticker,
                                      self._timeframe,
                                      self._since,
                                      self._untill)
