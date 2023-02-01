# backintime 1.6.3
✨ Инструмент для тестирования торговых стратегий на исторических данных ✨  
Такое тестирование не гарантирует те же результаты в реальной торговле, но дает примерную оценку успешности стратегии. Чем меньший таймфрейм используется, тем точнее получится результат.


> Ветка для новой версии (пока не вышла).  
  NB: Маржинальная торговля пока не поддерживается. Ожидается в релизах 2.x

## Способности
- Использует CSV или Binance API как источник данных
- Одни и те же данные могут быть представлены на разных таймфреймах (несколько свечей короткого таймфрейма используются чтобы представить свечку на более длинном таймфрейме)
- Поддерживаемые ордера: Market, Limit, Take Profit, Take Profit Limit, Stop Loss, Stop Loss Limit
- Встроенные индикаторы. Смотри [список](#индикаторы).
- Статистика сделок (win rate, profit/loss, avg. profit и т.д.) с поддержкой  FIFO, LIFO, AVCO алгоритмов расчета прибыли/убытка
- Экспорт оредров, сделок и статистики в csv


## Индикаторы
- MA - Moving Average
- EMA - Exponential Moving Average
- MACD - Moving Average Convergence Divergence
- BBANDS - Bollinger Bands
- RSI - Relative Strength Index
- ATR - Average True Range
- ADX - Average Directional Movement Index
- DMI - Directional Movement Indicator
- PIVOT - Pivot Points (Traditional, Fibonacci or Classic)


## Установка
```sh
python3 -m pip install backintime
```


## Как использовать

Пример со стратегией MACD приведен ниже. Стратегия покупает когда линия MACD пересекает сигнальную линию снизу вверх (т.е. гистограмма становится положительной), и продает когда линия MACD пересекает сигнальную сверху вниз. Эта стратегия дает  большой убыток и приведена здесь только как пример. Обычно в стратегиях не используется только один индикатор.
```py
from datetime import datetime
from backintime import TradingStrategy, run_backtest
from backintime.trading_strategy import TradingStrategy
from backintime.timeframes import Timeframes as tf
from backintime.indicator_params import MACD
from backintime.data.binance import BinanceCandlesFactory


class MacdStrategy(TradingStrategy): # (1)
    title = "Sample MACD Strategy"
    indicators = { MACD(tf.H1) }	# (2)

    def tick(self):	# (3)
        macd = self.analyser.macd(tf.H1)
        if not self.position and macd.crossover_up():
            self.buy()	# (4)
        elif self.position and macd.crossover_down():
            self.sell()	# (5)


feed = BinanceCandlesFactory('BTCUSDT', tf.M15)	# (6)
since = datetime.fromisoformat("2020-01-01 00:00+00:00")
until = datetime.fromisoformat("2021-01-01 00:00+00:00")

result = run_backtest(MacdStrategy, feed,
                      10_000, since, until, 
                      maker_fee='0.005', taker_fee='0.005')
print(result)
print(result.get_stats('FIFO'))
result.export()
```
Чтобы реализовать стратегию, нужно создать класс, отнаследованный от `TradingStrategy` (1), определить используемые индикаторы (2) и предоставить алгоритм в методе `tick` (3).
Когда соответствующие условия выполнены, стратегия вызывает методы `buy` (4) или `sell` (5) для выставления Market ордера.  
Здесь тестирование проводится с использованием свечей из API Binance на 15-минутном таймфрейме (6). Однако для повышения производительности можно использовать CSV файл.


---

Следующий пример со стратегией "Прорыв сопротивления SMA" демонстрирует более продвинутые возможности: лимитные, тейк-профит и стоп-лосс ордера. Стратегия покупает, когда последняя цена закрытия пересекает линию SMA снизу вверх, и продает на уровнях тейк-профита или стоп-лосса. В качестве фильтров используются сигналы MACD и DMI.
```py
import typing as t
from datetime import datetime
from decimal import Decimal
from backintime import TradingStrategy, run_backtest
from backintime.timeframes import Timeframes as tf
from backintime.data.binance import BinanceCandlesFactory
from backintime.indicator_params import SMA, MACD, DMI, PIVOT
from backintime.analyser.indicators.dmi import DMIResultSequence
from backintime.analyser.indicators.macd import MacdResultSequence
from backintime.broker import TakeProfitOptions, StopLossOptions


def macd_hist_up(macd: MacdResultSequence) -> bool:
    """True, if MACD hist > 0."""
    return macd[-1].hist > 0


def dmi_buy_signal(dmi: DMIResultSequence) -> bool:
    """True, if +DI > -DI."""
    return dmi.positive_di[-1] > dmi.negative_di[-1]


class SmaResistanceBreakout(TradingStrategy):
    title = "SMA resistance breakout"
    candle_timeframes = { tf.M15 }
    indicators = {
        SMA(tf.M15, 55),
        MACD(tf.M15),
        DMI(tf.M15, 14),
        PIVOT(tf.D1, 15)
    }

    def __init__(self, broker, analyser, candles):
        self.prev_close: t.Optional[Decimal] = None
        self.curr_close: t.Optional[Decimal] = None
        super().__init__(broker, analyser, candles)

    def tick(self):
        self.prev_close = self.curr_close
        self.curr_close = self.candles.get(tf.M15).close
        sma = self.analyser.sma(tf.M15, period=55)[-1]
        sma_crossover_up = self.curr_close > sma and \
                           self.prev_close and self.prev_close <= sma

        if self.broker.max_fiat_for_maker and sma_crossover_up and \
                macd_hist_up(self.analyser.macd(tf.M15)) and \
                dmi_buy_signal(self.analyser.dmi(tf.M15, 14)):
            # Calculate buy price: current SMA + 0.2%
            limit_price = Decimal(sma) * Decimal('1.002')
            # Set up TP at PIVOT' R2 level
            pivot = self.analyser.pivot(tf.D1, 15)
            take_profit_trigger = pivot[-1].r2
            take_profit = TakeProfitOptions(percentage_amount=Decimal('100.00'),
                                            trigger_price=take_profit_trigger)
            # Set up SL at current close price - 5%
            stop_loss_trigger = self.candles.get(tf.M15).close * Decimal('0.95')
            stop_loss = StopLossOptions(percentage_amount=Decimal('100.00'), 
                                        trigger_price=stop_loss_trigger)
            # Submit limit buy with TP & SL
            self.limit_buy(order_price=limit_price,
                           amount=self.broker.max_fiat_for_maker,
                           take_profit=take_profit,
                           stop_loss=stop_loss)


feed = BinanceCandlesFactory('BTCUSDT', tf.M15)
since = datetime.fromisoformat("2020-03-01 00:00+00:00")
until = datetime.fromisoformat("2021-05-01 00:00+00:00")

result = run_backtest(SmaResistanceBreakout, feed, 
                      10_000, since, until, 
                      maker_fee='0.005', taker_fee='0.005')

print(result)
print(result.get_stats('FIFO'))
print(result.get_stats('LIFO'))
print(result.get_stats('AVCO'))
result.export()

```

## Основные компоненты

Краткий обзор доступен [здесь] (англ.) 


## Кое-какие мысли

Я планирую добавить поддержку маржинальной торговли (позволит тестировать шортовые стратегии и стратегии, использующие плечи) и реализовать бэктестинг в виде event based системы, использующей очередь для коммуникации (позволит запускать бэктестинг на распределенных системах).


## Документация

Документации нет, потому что код еще не стабилен (но работает как ожидается). Пока что можно посмотреть исходники или использовать `help` в REPL.


## Лицензия

MIT


## Создатель

 Аким Мухтаров [@akim_int80h]


[@akim_int80h]: <https://t.me/akim_int80h>
[здесь]: <https://github.com/akim-mukhtarov/backintime/tree/v163#core-concepts>