from __future__ import annotations
import typing as t

import requests as r
from datetime import datetime, timezone
from collections import abc
from backintime.v163.data.candle import Candle
from backintime.v163.data.data_provider import DataProvider
from backintime.v163.timeframes import Timeframes as tf
from .utils import to_ms, parse_candle


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
                 until: datetime):
        self._ticker = ticker 
        self._tf = timeframe
        self._start_date = since
        self._end_date = until
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
        until = to_ms(self._end_date)

        max_per_request = 1000
        max_time_step = max_per_request*self.candle_duration()*1000
        params = {
            "symbol": self._ticker,
            "interval": self._interval,
            "startTime": None,
            "endTime": until,
            "limit": max_per_request
        }

        for start_time in range(since, until, max_time_step):
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
                 until: t.Optional[datetime]=datetime.now(timezone.utc)):
        self._ticker=ticker
        self._timeframe=timeframe
        self._since=since
        self._until=until

    def __iter__(self) -> BinanceCandlesIterator:
        return BinanceCandlesIterator(self._ticker,
                                      self._timeframe,
                                      self._since,
                                      self._until)

    def timeframe(self) -> Timeframe:
        return self._timeframe