from decimal import Decimal
from datetime import datetime, timezone
from backintime.data.candle import Candle
from backintime.broker.broker import Broker, OrderNotFound
from backintime.broker.fees import FeesEstimator
from backintime.broker.base import (
    OrderInfo, 
    BrokerException, 
    OrderSubmissionError,
    InvalidOrderData,
    InsufficientFunds,
    OrderCancellationError
)
from backintime.broker.orders import (
    Order, 
    OrderSide, 
    OrderStatus,
    OrderType, 
    MarketOrderFactory, 
    LimitOrderFactory, 
    TakeProfitFactory, 
    StopLossFactory
)


def test_max_fiat_for_taker():
    """
    Test estimation of max available fiat for a `taker` order.
    Fees are set to 0.5%.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    sample_value = Decimal(10_050)
    expected_value = Decimal(10_000)    # 99.5% from sample
    broker = Broker(sample_value, fees)
    assert broker.get_max_fiat_for_taker() == expected_value


def test_max_fiat_for_taker_no_fees():
    """
    Test estimation of max available fiat for a `taker` order.
    Fees are set to 0.
    """
    sample_value = Decimal(10_000)
    expected_value = sample_value
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(sample_value, fees)
    assert broker.get_max_fiat_for_taker() == expected_value


def test_max_fiat_for_maker():
    """
    Test estimation of max available fiat for a `maker` order.
    Fees are set to 0.5%.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    sample_value = Decimal(10_050)
    expected_value = Decimal(10_000)    # 99.5% from sample
    broker = Broker(sample_value, fees)
    assert broker.get_max_fiat_for_maker() == expected_value


def test_max_fiat_for_maker_no_fees():
    """
    Test estimation of max available fiat for a `maker` order.
    Fees are set to 0.
    """
    sample_value = Decimal(10_000)
    expected_value = sample_value
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(sample_value, fees)
    assert broker.get_max_fiat_for_maker() == expected_value


def test_available_fiat_after_market_buy_submission():
    """
    Check whether available fiat decreases properly 
    after submission of market buy order.
    """
    maker_fee = Decimal('0.010')
    taker_fee = Decimal('0.005')

    start_balance = Decimal(10_000)
    amount = Decimal(5_000)
    expected_value = start_balance - amount * (1 + taker_fee)
    
    broker = Broker(start_balance, FeesEstimator(maker_fee, taker_fee))
    broker.submit_order(MarketOrderFactory(OrderSide.BUY, amount))
    assert broker.balance.available_fiat_balance == expected_value


def test_market_order_submission():
    """Test submission of a valid market order."""
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    start_balance = Decimal(10_000)
    expected_value = start_balance - test_amount * (1 + taker_fee)

    expected_status = OrderStatus.CREATED
    expected_order_type = OrderType.MARKET
    expected_side = test_side
    expected_amount = test_amount
    expected_fee = None
    expected_fill_price = None

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)

    market_order = MarketOrderFactory(test_side, test_amount)
    market_order = broker.submit_market_order(market_order)
    available_fiat = broker.balance.available_fiat_balance

    assert market_order.status is expected_status and \
            market_order.order_type is expected_order_type and \
            market_order.order_side is expected_side and \
            market_order.amount == expected_amount and \
            market_order.trading_fee == expected_fee and \
            market_order.fill_price == expected_fill_price and \
            available_fiat == expected_value


def test_market_order_submission_with_max_fiat():
    """Test submission of a valid market order with max available fiat."""
    test_side = OrderSide.BUY
    start_balance = Decimal(10_050)
    expected_value = 0

    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(start_balance, fees)
    test_amount = broker.get_max_fiat_for_taker()

    expected_status = OrderStatus.CREATED
    expected_order_type = OrderType.MARKET
    expected_side = test_side
    expected_amount = test_amount
    expected_fee = None
    expected_fill_price = None

    market_order = MarketOrderFactory(test_side, test_amount)
    market_order = broker.submit_market_order(market_order)
    available_fiat = broker.balance.available_fiat_balance

    assert market_order.status is expected_status and \
            market_order.order_type is expected_order_type and \
            market_order.order_side is expected_side and \
            market_order.amount == expected_amount and \
            market_order.trading_fee == expected_fee and \
            market_order.fill_price == expected_fill_price and \
            available_fiat == expected_value


def test_invalid_market_order_submission():
    """Test market order submission with invalid data."""
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_order_data_raised = False

    market_order = MarketOrderFactory(OrderSide.BUY, invalid_amount)
    try:
        market_order = broker.submit_market_order(market_order)
    except InvalidOrderData:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_market_order_submission_insufficient_funds():
    """
    Test market order submission with insufficient funds.
    Fees are set to 0.5%.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    insufficient_funds_raised = False

    market_order = MarketOrderFactory(OrderSide.BUY, Decimal(10_000))
    try:
        market_order = broker.submit_market_order(market_order)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


def test_market_order_submission_insufficient_funds_no_fees():
    """
    Test market order submission with insufficient funds.
    Fees are set to 0.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    insufficient_funds_raised = False
    
    market_order = MarketOrderFactory(OrderSide.BUY, Decimal(20_000))
    try:
        market_order = broker.submit_market_order(market_order)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


def test_market_order_execution():
    """Test execution of a valid market order."""
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    start_balance = Decimal(10_050)
    expected_value = 0

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.get_max_fiat_for_taker()   # 10_000
    
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

    market_order = MarketOrderFactory(test_side, test_amount)
    market_order = broker.submit_market_order(market_order)
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


def test_market_order_cancellation():
    """Test cancellation of a valid market order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)
    market_order = MarketOrderFactory(test_side, test_amount)
    market_order = broker.submit_market_order(market_order)
    broker.cancel_order(market_order.order_id)
    
    available_fiat_balance = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    assert market_order.status is expected_status and \
            available_fiat_balance == expected_fiat and \
            fiat_balance == expected_fiat


def test_limit_order_submission():
    """Test submission of a valid limit order."""
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)

    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_order_price = Decimal(15_000)

    expected_status = OrderStatus.CREATED
    expected_order_type = OrderType.LIMIT
    expected_side = test_side
    expected_amount = test_amount
    expected_price = test_order_price
    expected_fee = None
    expected_fill_price = None

    limit_order = LimitOrderFactory(test_side, 
                                    test_amount, 
                                    test_order_price)
    limit_order = broker.submit_limit_order(limit_order)
    assert limit_order.status is expected_status and \
            limit_order.order_type is expected_order_type and \
            limit_order.order_side is expected_side and \
            limit_order.amount == expected_amount and \
            limit_order.order_price == expected_price and \
            limit_order.trading_fee == expected_fee and \
            limit_order.fill_price == expected_fill_price


def test_limit_order_submission_with_max_fiat():
    """Test submission of a valid limit order with max available fiat."""
    test_side = OrderSide.BUY
    start_balance = Decimal(10_050)
    test_order_price = Decimal(15_000)
    expected_value = 0

    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(start_balance, fees)
    test_amount = broker.get_max_fiat_for_maker()

    expected_status = OrderStatus.CREATED
    expected_order_type = OrderType.LIMIT
    expected_side = test_side
    expected_amount = test_amount
    expected_price = test_order_price
    expected_fee = None
    expected_fill_price = None

    limit_order = LimitOrderFactory(test_side, 
                                    test_amount, 
                                    test_order_price)
    limit_order = broker.submit_limit_order(limit_order)
    assert limit_order.status is expected_status and \
            limit_order.order_type is expected_order_type and \
            limit_order.order_side is expected_side and \
            limit_order.amount == expected_amount and \
            limit_order.order_price == expected_price and \
            limit_order.trading_fee == expected_fee and \
            limit_order.fill_price == expected_fill_price


def test_limit_order_submission_with_invalid_take_profit():
    """
    Check whether an attempt to submit valid limit order with
    invalid take profit will raise `InvalidOrderData`.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_trigger = Decimal(-12_000)
    invalid_limit = Decimal(-15_000)
    invalid_order_data_raised = False

    invalid_tp_factory = TakeProfitFactory(invalid_amount,
                                           invalid_trigger,
                                           invalid_limit)

    limit_order = LimitOrderFactory(OrderSide.BUY, 
                                    Decimal(5_000), 
                                    Decimal(5_000),
                                    invalid_tp_factory)
    try:
        limit_order = broker.submit_limit_order(limit_order)
    except InvalidOrderData:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_with_invalid_stop_loss():
    """
    Check whether an attempt to submit valid limit order with
    invalid stop loss will raise `InvalidOrderData`.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_trigger = Decimal(-12_000)
    invalid_limit = Decimal(-15_000)
    invalid_order_data_raised = False

    invalid_sl_factory = StopLossFactory(invalid_amount,
                                         invalid_trigger,
                                         invalid_limit)

    limit_order = LimitOrderFactory(OrderSide.BUY, 
                                    Decimal(5_000), 
                                    Decimal(5_000),
                                    None,
                                    invalid_sl_factory)
    try:
        limit_order = broker.submit_limit_order(limit_order)
    except InvalidOrderData:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_with_invalid_tpsl():
    """
    Test submission of a valid limit order with invalid 
    params for take profit and stop loss orders.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_trigger = Decimal(-12_000)
    invalid_limit = Decimal(-15_000)
    invalid_order_data_raised = False

    invalid_tp_factory = TakeProfitFactory(invalid_amount,
                                           invalid_trigger,
                                           invalid_limit)

    invalid_sl_factory = StopLossFactory(invalid_amount,
                                         invalid_trigger,
                                         invalid_limit)

    limit_order = LimitOrderFactory(OrderSide.BUY, 
                                    Decimal(5_000), 
                                    Decimal(5_000),
                                    invalid_tp_factory,
                                    invalid_sl_factory)
    try:
        limit_order = broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_invalid_limit_order_submission():
    """
    Test submission of invalid limit order 
    (`amount` and `order_price` <= 0).
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_limit = Decimal(-15_000)
    invalid_order_data_raised = False

    limit_order = LimitOrderFactory(OrderSide.BUY, 
                                    invalid_amount, 
                                    invalid_limit)
    try:
        limit_order = broker.submit_limit_order(limit_order)
    except InvalidOrderData:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_insufficient_funds_no_fees():
    """
    Test limit order submission with insufficient funds.
    Fees are set to 0.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    test_amount = Decimal(20_000)
    insufficient_funds_raised = False

    limit_order = LimitOrderFactory(OrderSide.BUY, 
                                    test_amount, 
                                    Decimal(25_000))
    try:
        limit_order = broker.submit_limit_order(limit_order)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


def test_limit_order_submission_insufficient_funds():
    """
    Test limit order submission with insufficient funds.
    Fees are set to 0.5%.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    test_amount = Decimal(10_000)
    insufficient_funds_raised = False

    limit_order = LimitOrderFactory(OrderSide.BUY, 
                                    test_amount, 
                                    Decimal(15_000))
    try:
        limit_order = broker.submit_limit_order(limit_order)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


def test_limit_order_execution_no_tpsl():
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    test_order_price = 1000
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.get_max_fiat_for_maker()   # 10_000
    
    test_candle = Candle(open_time=datetime.now(),
                         open=Decimal(500),
                         high=Decimal(1100),
                         low=Decimal(400),
                         close=Decimal(1050),
                         close_time=datetime.now(),
                         volume=Decimal(10_000))

    expected_status = OrderStatus.EXECUTED
    expected_fee = start_balance - test_amount  # 50
    expected_fill_price = test_order_price      # 1000
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 10
    expected_crypto_balance = 10

    limit_order = LimitOrderFactory(test_side, 
                                    test_amount, 
                                    test_order_price)
    limit_order = broker.submit_limit_order(limit_order)
    broker.update(test_candle)

    available_fiat = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    available_crypto = broker.balance.available_crypto_balance
    crypto_balance = broker.balance.crypto_balance

    assert limit_order.status is expected_status and \
            limit_order.trading_fee == expected_fee and \
            limit_order.fill_price == expected_fill_price and \
            limit_order.fill_price == limit_order.order_price and \
            available_fiat == expected_available_fiat and \
            fiat_balance == expected_fiat_balance and \
            available_crypto == expected_available_crypto and \
            crypto_balance == expected_crypto_balance


def test_limit_order_execution_and_take_profit_limit_activation():
    maker_fee = Decimal('0.005')
    taker_fee = Decimal('0.005')
    test_side = OrderSide.BUY
    test_order_price = 1000
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.get_max_fiat_for_maker()   # 10_000
    
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
               close=Decimal(1200),
               close_time=datetime.now(),
               volume=Decimal(10_000))
    ]

    expected_take_profit_status = OrderStatus.ACTIVATED
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 0
    expected_crypto_balance = 10

    tp_factory = TakeProfitFactory(amount=10,
                                   trigger_price=1200,
                                   order_price=1500)

    limit_order = LimitOrderFactory(test_side,          # BUY
                                    test_amount,        # 10_000
                                    test_order_price,   # 1000
                                    tp_factory)
    limit_order = broker.submit_limit_order(limit_order)

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
    test_order_price = 1000
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.get_max_fiat_for_maker()   # 10_000
    
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
               open=Decimal(900),
               high=Decimal(1000),
               low=Decimal(800),
               close=Decimal(850),
               close_time=datetime.now(),
               volume=Decimal(10_000))
    ]

    expected_stop_loss_status = OrderStatus.ACTIVATED
    expected_available_fiat = 0
    expected_fiat_balance = 0
    expected_available_crypto = 0
    expected_crypto_balance = 10

    sl_factory = StopLossFactory(amount=10,
                                 trigger_price=900,
                                 order_price=700)

    order = LimitOrderFactory(
                test_side,          # BUY
                test_amount,        # 10_000
                test_order_price,   # 1000
                stop_loss_factory=sl_factory)

    order = broker.submit_limit_order(order)
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
    test_order_price = 1000
    start_balance = Decimal(10_050)

    fees = FeesEstimator(maker_fee, taker_fee)
    broker = Broker(start_balance, fees)
    test_amount = broker.get_max_fiat_for_maker()   # 10_000
    
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
    expected_crypto_balance = 10

    tp_factory = TakeProfitFactory(amount=10,
                                   trigger_price=1000,
                                   order_price=1500)

    sl_factory = StopLossFactory(amount=10,
                                 trigger_price=900,
                                 order_price=500)

    order = LimitOrderFactory(test_side,          # BUY
                              test_amount,        # 10_000
                              test_order_price,   # 1000
                              tp_factory,
                              sl_factory)

    order = broker.submit_limit_order(order)
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


def test_limit_order_cancellation():
    """Test cancellation of a limit order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)
    limit_order = LimitOrderFactory(test_side, 
                                    test_amount, 
                                    Decimal(15_000))
    limit_order = broker.submit_limit_order(limit_order)
    broker.cancel_order(limit_order.order_id)

    available_fiat_balance = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    assert limit_order.status is expected_status and \
            available_fiat_balance == expected_fiat and \
            fiat_balance == expected_fiat


def test_invalid_take_profit_order_submission():
    """
    Check whether an attempt to submist invalid take profit order
    (`amount`, `trigger_price` and `order_price` <= 0) will raise
    `InvalidOrderData`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_limit = Decimal(-15_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    tp = TakeProfitFactory(invalid_amount,
                           invalid_trigger,
                           invalid_limit)
    try:
        tp = broker.submit_take_profit_order(OrderSide.SELL, tp)
    except InvalidOrderData:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_take_profit_order_submission_insufficient_funds():
    """
    Check whether an attempt to submit take profit 
    with insufficient funds will raise `InsufficientFunds`.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    test_amount = Decimal(10_000)
    insufficient_funds_raised = False

    tp = TakeProfitFactory(test_amount,
                           Decimal(12_000),
                           Decimal(12_500))
    try:
        tp = broker.submit_take_profit_order(OrderSide.BUY, tp)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


def test_take_profit_order_cancellation():
    """Test cancellation of a valid take profit order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)

    tp = TakeProfitFactory(test_amount,
                           Decimal(1_000),
                           Decimal(500))
    tp = broker.submit_take_profit_order(test_side, tp)
    broker.cancel_order(tp.order_id)

    available_fiat_balance = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    assert tp.status is expected_status and \
            available_fiat_balance == expected_fiat and \
            fiat_balance == expected_fiat


def test_invalid_stop_loss_order_submission():
    """
    Check whether an attempt to submist invalid stop loss order
    (`amount`, `trigger_price` and `order_price` <= 0) will raise
    `InvalidOrderData`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_limit = Decimal(-15_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    sl = StopLossFactory(invalid_amount,
                         invalid_trigger,
                         invalid_limit)
    try:
        sl = broker.submit_stop_loss_order(OrderSide.SELL, sl)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_stop_loss_order_submission_insufficient_funds():
    """
    Check whether an attempt to submit stop loss
    with insufficient funds will raise `InsufficientFunds`."""
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    test_amount = Decimal(10_000)
    insufficient_funds_raised = False

    sl = StopLossFactory(test_amount,
                         Decimal(12_000),
                         Decimal(12_500))
    try:
        sl = broker.submit_stop_loss_order(OrderSide.BUY, sl)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


def test_stop_loss_order_cancellation():
    """Test cancellation of a valid stop loss order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)

    sl = StopLossFactory(test_amount,
                         Decimal(1_000),
                         Decimal(500))
    sl = broker.submit_stop_loss_order(test_side, sl)
    broker.cancel_order(sl.order_id)
    
    available_fiat_balance = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    assert sl.status is expected_status and \
            available_fiat_balance == expected_fiat and \
            fiat_balance == expected_fiat


def test_order_cancellation_with_wrong_id():
    """
    Check whether an attempt to cancel order with wrong id 
    will raise `OrderCancellationError`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    wrong_id = 0
    order_cancellation_error_raised = False

    try:
        broker.cancel_order(wrong_id)
    except OrderCancellationError:
        order_cancellation_error_raised = True
    assert order_cancellation_error_raised


def test_cancel_already_cancelled():
    """
    Check whether an attempt to cancel already cancelled order 
    will raise `OrderCancellationError`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    order_cancellation_error_raised = False

    market_order = MarketOrderFactory(OrderSide.BUY, Decimal(10_000))
    market_order = broker.submit_market_order(market_order)
    broker.cancel_order(market_order.order_id)

    try:
        broker.cancel_order(market_order.order_id)
    except OrderCancellationError:
        order_cancellation_error_raised = True
    assert order_cancellation_error_raised
