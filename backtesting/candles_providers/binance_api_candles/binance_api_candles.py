from .utils import to_ms, to_candle
from ..api_candles import ApiCandles
from ...timeframes import Timeframes
import datetime, time
import requests as r


class BinanceApiCandles(ApiCandles):

    _url = 'https://api.binance.com/api/v3/klines'
    # <Timeframes> : <str - binance str repr>
    _binance_intervals = {
        Timeframes.M1: '1m',
        Timeframes.M3: '3m',
        Timeframes.M5: '5m',
        Timeframes.M15: '15m',
        Timeframes.M30: '30m',
        Timeframes.H1: '1h',
        Timeframes.H2: '2h',
        Timeframes.H4: '4h',
        Timeframes.D1: '1d',
        Timeframes.W1: '1w'
    }

    def __init__(self, ticker: str, timeframe_tag: Timeframes):
        try:
            self._interval = self._binance_intervals[timeframe_tag]
        except KeyError:
            allowed = list(self._binance_intervals.keys())
            raise ValueError(
                'Binance API supports the following timeframes: {allowed}')

        self._ticker = ticker
        self._gen = None
        super().__init__(timeframe_tag)

    def _candles(self):
        # Convert datetime objects to timestamp
        since = to_ms(self._start_date.timestamp())
        end_time = to_ms(time.time())

        MAX_PER_REQUEST = 1000
        max_time_step = MAX_PER_REQUEST*self.candle_duration()*1000

        params = {
            'symbol': self._ticker,
            'interval': self._interval,
            'startTime': None,
            'endTime': end_time,
            'limit': MAX_PER_REQUEST
        }

        for start_time in range(since, end_time, max_time_step):
            # this requests 1k candles at a time
            params['startTime'] = start_time
            res = r.get(self._url, params)
            res.raise_for_status()
            for obj in res.json():
                yield to_candle(obj, self._candle_buffer)

    def current_date(self) -> datetime.datetime:
        if not self._start_date:
            return None
        ticks = self.get_ticks()
        time_passed = datetime.timedelta(
            seconds=ticks*self.candle_duration())
        return self._start_date + time_passed

    def next(self) -> None:
        if not self._gen:
            self._gen = iter(self._candles())
        next(self._gen)
        self._tick_counter.increment()
