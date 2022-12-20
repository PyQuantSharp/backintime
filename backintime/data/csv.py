from __future__ import annotations

import csv
import typing as t
import pandas as pd 
from itertools import dropwhile
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from dataclasses import dataclass
from collections import abc
from backintime.timeframes import Timeframes
from .data_provider import (
    Candle,
    DataProvider, 
    DataProviderFactory, 
    DataProviderError,
    ParsingError
)


@dataclass
class CSVCandlesSchema:
    """Schema specifies column indexes in CSV file."""
    open_time: int 
    open: int 
    high: int 
    low: int 
    close: int 
    close_time: int
    volume: t.Optional[int]=None


class DateNotFound(DataProviderError):
    def __init__(self, date: datetime, filename: str):
        message = f"Date {date} was not found in {filename}"
        super().__init__(message)


class InconsistentData(DataProviderError):
    def __init__(self, open_time: datetime, prev_open_time: datetime):
        message = f"Candle {open_time} follows {prev_open_time}"
        super().__init__(message)


def _parse_volume(candle, schema: CSVCandlesSchema) -> Decimal:
    return Decimal(candle[schema.volume]) if schema.volume \
        else Decimal('NaN')


def _parse_candle(candle, schema: CSVCandlesSchema, date_parser) -> Candle:
    """Parse candle from a sequence of strings."""
    try:
        return Candle(open_time=date_parser(candle[schema.open_time]),
                      open=Decimal(candle[schema.open]),
                      high=Decimal(candle[schema.high]),
                      low=Decimal(candle[schema.low]),
                      close=Decimal(candle[schema.close]),
                      volume=_parse_volume(candle, schema),
                      close_time=date_parser(candle[schema.close_time]))
    except Exception as e:
        raise ParsingError(str(e))


def _skip_to_date(rows: t.Iterable[t.Iterable[str]], 
                  column_index: int, 
                  date: datetime,
                  parse_date: t.Callable) -> t.Iterable[t.Iterable[str]]:
    """Skip rows until date at `column_index` equals `date`."""
    predicate = lambda row: parse_date(row[column_index]) != date
    return dropwhile(predicate, rows)


def _skip_headers(rows: t.Iterable[str]) -> t.Iterable[str]:
    """Skip rows that begin with non-numeric char."""
    return dropwhile(lambda row: row[0][0].isalpha(), rows)


def _csvrows(filename: str, 
             delimiter: str, 
             quotechar: str) -> t.Generator[t.Iterable[str], None, None]:
    """Return generator that will iterate over rows in CSV file."""
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, 
                            quotechar=quotechar)
        for row in reader:
            yield row


class CSVCandles(DataProvider):
    def __init__(self, 
                 filename: str,
                 symbol: str,
                 timeframe: Timeframes,
                 schema: CSVCandlesSchema, 
                 delimiter: str,
                 quotechar: str,
                 since: datetime, 
                 until: datetime,
                 date_parser: t.Callable):
        self._filename = filename
        self._symbol = symbol
        self._timeframe = timeframe
        self._schema = schema
        self._delimiter = delimiter
        self._quotechar = quotechar
        self._since = since
        self._until = until
        self._date_parser = date_parser

    def __iter__(self) -> t.Iterator[Candle]:
        """Return generator that will yield one candle at a time."""
        csvrows = _csvrows(self._filename, self._delimiter, self._quotechar)
        csvrows = _skip_headers(csvrows)
        csvrows = _skip_to_date(csvrows, self._schema.open_time, 
                                self._since, self._date_parser)
        csvrows = iter(csvrows)
        prev_open: t.Optional[datetime] = None
        # Check whether date present
        try:
            row = next(csvrows)
        except StopIteration:
            raise DateNotFound(self._since, self._filename)
        else:
            candle = _parse_candle(row, self._schema, self._date_parser)
            prev_open = candle.open_time
            yield candle

        for row in csvrows:
            candle = _parse_candle(row, self._schema, self._date_parser)
            if candle.open_time >= self._until:
                raise StopIteration()
            # Check data consistency
            delta = candle.open_time - prev_open
            delta = delta.total_seconds()
            if delta < self._timeframe.value:
                raise InconsistentData(candle.open_time, prev_open)
            prev_open = candle.open_time
            yield candle

    @property
    def title(self) -> str:
        return f"local CSV file {self._filename}"

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def timeframe(self) -> Timeframes:
        return self._timeframe


def _utcnow() -> datetime:
    """Return current timezone aware date (UTC)."""
    return datetime.now(timezone.utc)


def _default_schema() -> CSVCandlesSchema:
    return CSVCandlesSchema(open_time=0, open=1,
                            high=2, low=3, close=4,
                            close_time=5, volume=6)


class CSVCandlesFactory(DataProviderFactory):
    def __init__(self, 
                 filename: str,
                 symbol: str,
                 timeframe: Timeframes,
                 schema: CSVCandlesSchema=_default_schema(),
                 delimiter=';',
                 quotechar='|',
                 date_parser=lambda x: pd.to_datetime(x, utc=True)):
        self.filename = filename
        self.symbol = symbol
        self.tf = timeframe
        self.schema = schema
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.date_parser = date_parser

    @property
    def timeframe(self) -> Timeframes:
        return self.tf

    def create(self, 
               since: datetime, 
               until: t.Optional[datetime]=_utcnow()) -> CSVCandles:
        return CSVCandles(self.filename, self.symbol, 
                          self.timeframe, self.schema, 
                          self.delimiter, self.quotechar, 
                          since, until, self.date_parser)
