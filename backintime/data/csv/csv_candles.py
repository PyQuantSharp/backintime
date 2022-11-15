from __future__ import annotations

import typing as t
from datetime import datetime, timezone
from dataclasses import dataclass
from collections import abc
from backintime.v163.data.data_provider import DataProvider, Candle
from .utils import parse_candle


@dataclass
class CSVCandlesSchema:
	open_time: int 
	open: int 
	high: int 
	low: int 
	close: int 
	close_time: int
	volume: t.Optional[int]


class CSVCandlesIterator(abc.Iterator):
	def __iter__(self) -> CSVCandlesIterator:
		return self

	def __next__(self) -> Candle:
		candle = next(self._get_candles)
		return parse_candle(candle, self._schema)


class CSVCandles(DataProvider):
	def __init__(self, 
				 filename: str,
				 timeframe: tf,
				 schema: CSVCandlesSchema, 
				 since: datetime, 
				 until: t.Optional[datetime]=datetime.now(timezone.utc)):
		pass

	def __iter__(self) -> CSVCandlesIterator:
		pass 