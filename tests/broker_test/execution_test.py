from decimal import Decimal
from datetime import datetime, timezone
from backintime.data.candle import Candle
from backintime.broker.default.broker import Broker, OrderNotFound
from backintime.broker.default.fees import FeesEstimator
from backintime.broker.base import (
    OrderSide,
    OrderType,
    OrderStatus,
    MarketOrderOptions, 
    LimitOrderOptions, 
    TakeProfitOptions, 
    StopLossOptions,
    BrokerException, 
    OrderSubmissionError,
    InvalidOrderData,
    InsufficientFunds,
    OrderCancellationError
)


def test_market_order_execution():
    """Test execution of a valid Market order."""
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    start_balance = Decimal(10_050)
    expected_value = 0

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.max_fiat_for_taker   # 10_000

    test_candle = Candle(open_time=datetime.now(),
                         open=Decimal(1000),
                         high=Decimal(1100),
                         low=Decimal(900),
                         close=Decimal(1050),
                         close_time=datetime.now(),
                         volume=Decimal(10_000))

    expected_status = OrderStatus.EXECUTED
    expected_fee = start_balance - test_amount  # 50
    expected_fill_price = test_candle.open      # 1000
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 10
    expected_crypto_balance = 10

    options = MarketOrderOptions(test_side, test_amount)
    market_order = broker.submit_market_order(options)
    broker.update(test_candle)

    available_fiat = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    available_crypto = broker.balance.available_crypto_balance
    crypto_balance = broker.balance.crypto_balance

    assert market_order.status is expected_status and \
            market_order.trading_fee == expected_fee and \
            market_order.fill_price == expected_fill_price and \
            available_fiat == expected_available_fiat and \
            fiat_balance == expected_fiat_balance and \
            available_crypto == expected_available_crypto and \
            crypto_balance == expected_crypto_balance


def test_limit_order_execution_no_tpsl():
    """Test execution of a valid Limit order."""
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    test_order_price = Decimal(1000)
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.max_fiat_for_maker   # 10_000

    test_candle = Candle(open_time=datetime.now(),
                         open=Decimal(500),
                         high=Decimal(1100),
                         low=Decimal(400),
                         close=Decimal(1050),
                         close_time=datetime.now(),
                         volume=Decimal(10_000))

    expected_status = OrderStatus.EXECUTED
    expected_fee = start_balance - test_amount  # 50
    expected_fill_price = Decimal(500)          # OPEN price
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 20
    expected_crypto_balance = 20

    options = LimitOrderOptions(test_side, 
                                amount=test_amount, 
                                order_price=test_order_price)
    limit_order = broker.submit_limit_order(options)
    broker.update(test_candle)

    available_fiat = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    available_crypto = broker.balance.available_crypto_balance
    crypto_balance = broker.balance.crypto_balance

    assert limit_order.status is expected_status and \
            limit_order.trading_fee == expected_fee and \
            limit_order.fill_price == expected_fill_price and \
            limit_order.fill_price <= limit_order.order_price and \
            available_fiat == expected_available_fiat and \
            fiat_balance == expected_fiat_balance and \
            available_crypto == expected_available_crypto and \
            crypto_balance == expected_crypto_balance


def test_limit_order_execution_and_take_profit_limit_activation():
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    test_order_price = Decimal(1000)
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.max_fiat_for_maker   # 10_000

    test_candles = [
        # One for limit execution
        Candle(open_time=datetime.now(),
               open=Decimal(500),
               high=Decimal(1100),
               low=Decimal(400),
               close=Decimal(1050),
               close_time=datetime.now(),
               volume=Decimal(10_000)),
        # Another for TP activation
        Candle(open_time=datetime.now(),
               open=Decimal(1000),
               high=Decimal(1500),
               low=Decimal(900),
               close=Decimal(1300),
               close_time=datetime.now(),
               volume=Decimal(10_000))
    ]

    expected_take_profit_status = OrderStatus.ACTIVATED
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 0
    expected_crypto_balance = 20

    tp_options = TakeProfitOptions(percentage_amount=Decimal('100.00'),
                                   trigger_price=Decimal(1200),
                                   order_price=Decimal(1500))

    options = LimitOrderOptions(test_side,                      # BUY
                                amount=test_amount,             # 10_000
                                order_price=test_order_price,   # 1000
                                take_profit=tp_options)
    limit_order = broker.submit_limit_order(options)

    for candle in test_candles:
        broker.update(candle)

    available_fiat = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    available_crypto = broker.balance.available_crypto_balance
    crypto_balance = broker.balance.crypto_balance
    take_profit_status = limit_order.take_profit.status

    assert take_profit_status is expected_take_profit_status and \
            available_fiat == expected_available_fiat and \
            fiat_balance == expected_fiat_balance and \
            available_crypto == expected_available_crypto and \
            crypto_balance == expected_crypto_balance


def test_limit_order_execution_and_stop_loss_limit_activation():
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    test_order_price = Decimal(500)
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.max_fiat_for_maker   # 10_000

    test_candles = [
        # One for limit execution
        Candle(open_time=datetime.now(),
               open=Decimal(1000),
               high=Decimal(1100),
               low=Decimal(400),
               close=Decimal(1050),
               close_time=datetime.now(),
               volume=Decimal(10_000)),
        # Another for SL activation
        Candle(open_time=datetime.now(),
               open=Decimal(1050),
               high=Decimal(1100),
               low=Decimal(890),
               close=Decimal(890),
               close_time=datetime.now(),
               volume=Decimal(10_000))
    ]

    expected_stop_loss_status = OrderStatus.ACTIVATED
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 0
    expected_crypto_balance = 25

    sl_options = StopLossOptions(percentage_amount=Decimal('100.00'),
                                 trigger_price=Decimal(900),
                                 order_price=Decimal(895))

    options = LimitOrderOptions(test_side,                      # BUY
                                amount=test_amount,             # 10_000
                                order_price=test_order_price,   # 500
                                stop_loss=sl_options)

    order = broker.submit_limit_order(options)
    for candle in test_candles:
        broker.update(candle)

    available_fiat = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    available_crypto = broker.balance.available_crypto_balance
    crypto_balance = broker.balance.crypto_balance
    stop_loss_status = order.stop_loss.status

    assert stop_loss_status is expected_stop_loss_status and \
            available_fiat == expected_available_fiat and \
            fiat_balance == expected_fiat_balance and \
            available_crypto == expected_available_crypto and \
            crypto_balance == expected_crypto_balance


def test_limit_order_execution_and_tpsl_activation():
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    test_order_price = Decimal(500)
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.max_fiat_for_maker   # 10_000

    test_candles = [
        # One for limit execution
        Candle(open_time=datetime.now(),
               open=Decimal(1000),
               high=Decimal(1100),
               low=Decimal(400),
               close=Decimal(1050),
               close_time=datetime.now(),
               volume=Decimal(10_000)),
        # Another for TP/SL activation
        Candle(open_time=datetime.now(),
               open=Decimal(900),
               high=Decimal(1000),
               low=Decimal(800),
               close=Decimal(850),
               close_time=datetime.now(),
               volume=Decimal(10_000))
    ]

    expected_take_profit_status = OrderStatus.ACTIVATED
    expected_stop_loss_status = OrderStatus.ACTIVATED
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 0
    expected_crypto_balance = 25

    tp_options = TakeProfitOptions(percentage_amount=Decimal('100.00'),
                                   trigger_price=Decimal(1000),
                                   order_price=Decimal(1500))

    sl_options = StopLossOptions(percentage_amount=Decimal('100.00'),
                                 trigger_price=Decimal(1000),
                                 order_price=Decimal(900))

    options = LimitOrderOptions(test_side,                      # BUY
                                amount=test_amount,             # 10_000
                                order_price=test_order_price,   # 500
                                take_profit=tp_options,
                                stop_loss=sl_options)

    order = broker.submit_limit_order(options)
    for candle in test_candles:
        broker.update(candle)

    available_fiat = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    available_crypto = broker.balance.available_crypto_balance
    crypto_balance = broker.balance.crypto_balance
    take_profit_status = order.take_profit.status
    stop_loss_status = order.stop_loss.status

    assert take_profit_status is expected_take_profit_status and \
            stop_loss_status is expected_stop_loss_status and \
            available_fiat == expected_available_fiat and \
            fiat_balance == expected_fiat_balance and \
            available_crypto == expected_available_crypto and \
            crypto_balance == expected_crypto_balance
