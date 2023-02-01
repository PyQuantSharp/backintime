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


def test_max_fiat_for_taker():
    """
    Test estimation of max available fiat for a `taker` order.
    Fees are set to 0.5%.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    sample_value = Decimal(10_050)
    expected_value = Decimal(10_000)    # 99.5% from sample
    broker = Broker(sample_value, fees)
    assert broker.max_fiat_for_taker == expected_value


def test_max_fiat_for_taker_no_fees():
    """
    Test estimation of max available fiat for a `taker` order.
    Fees are set to 0.
    """
    sample_value = Decimal(10_000)
    expected_value = sample_value
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(sample_value, fees)
    assert broker.max_fiat_for_taker == expected_value


def test_max_fiat_for_maker():
    """
    Test estimation of max available fiat for a `maker` order.
    Fees are set to 0.5%.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    sample_value = Decimal(10_050)
    expected_value = Decimal(10_000)    # 99.5% from sample
    broker = Broker(sample_value, fees)
    assert broker.max_fiat_for_maker == expected_value


def test_max_fiat_for_maker_no_fees():
    """
    Test estimation of max available fiat for a `maker` order.
    Fees are set to 0.
    """
    sample_value = Decimal(10_000)
    expected_value = sample_value
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(sample_value, fees)
    assert broker.max_fiat_for_maker == expected_value


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

    options = MarketOrderOptions(test_side, test_amount)
    market_order = broker.submit_market_order(options)
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
    test_amount = broker.max_fiat_for_taker

    expected_status = OrderStatus.CREATED
    expected_order_type = OrderType.MARKET
    expected_side = test_side
    expected_amount = test_amount
    expected_fee = None
    expected_fill_price = None

    options = MarketOrderOptions(test_side, test_amount)
    market_order = broker.submit_market_order(options)
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

    options = MarketOrderOptions(OrderSide.BUY, invalid_amount)
    try:
        broker.submit_market_order(options)
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

    options = MarketOrderOptions(OrderSide.BUY, Decimal(10_000))
    try:
        broker.submit_market_order(options)
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

    options = MarketOrderOptions(OrderSide.BUY, Decimal(20_000))
    try:
        broker.submit_market_order(options)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


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

    options = LimitOrderOptions(test_side, 
                                amount=test_amount, 
                                order_price=test_order_price)
    limit_order = broker.submit_limit_order(options)

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
    test_amount = broker.max_fiat_for_maker

    expected_status = OrderStatus.CREATED
    expected_order_type = OrderType.LIMIT
    expected_side = test_side
    expected_amount = test_amount
    expected_price = test_order_price
    expected_fee = None
    expected_fill_price = None

    options = LimitOrderOptions(test_side, 
                                amount=test_amount, 
                                order_price=test_order_price)
    limit_order = broker.submit_limit_order(options)

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

    invalid_tp_options = TakeProfitOptions(amount=invalid_amount,
                                           trigger_price=invalid_trigger,
                                           order_price=invalid_limit)

    options = LimitOrderOptions(OrderSide.BUY, 
                                amount=Decimal(5_000),
                                order_price=Decimal(5_000),
                                take_profit=invalid_tp_options)
    try:
        broker.submit_limit_order(options)
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

    invalid_sl_options = StopLossOptions(amount=invalid_amount,
                                         trigger_price=invalid_trigger,
                                         order_price=invalid_limit)

    options = LimitOrderOptions(OrderSide.BUY, 
                                amount=Decimal(5_000), 
                                order_price=Decimal(5_000),
                                stop_loss=invalid_sl_options)
    try:
        broker.submit_limit_order(options)
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

    invalid_tp_options = TakeProfitOptions(amount=invalid_amount,
                                           trigger_price=invalid_trigger,
                                           order_price=invalid_limit)

    invalid_sl_options = StopLossOptions(amount=invalid_amount,
                                         trigger_price=invalid_trigger,
                                         order_price=invalid_limit)

    options = LimitOrderOptions(OrderSide.BUY, 
                                amount=Decimal(5_000), 
                                order_price=Decimal(5_000),
                                take_profit=invalid_tp_options,
                                stop_loss=invalid_sl_options)
    try:
        broker.submit_limit_order(options)
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

    options = LimitOrderOptions(OrderSide.BUY, 
                                amount=invalid_amount, 
                                order_price=invalid_limit)
    try:
        broker.submit_limit_order(options)
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

    options = LimitOrderOptions(OrderSide.BUY, 
                                amount=test_amount, 
                                order_price=Decimal(25_000))
    try:
        broker.submit_limit_order(options)
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

    options = LimitOrderOptions(OrderSide.BUY, 
                                amount=test_amount, 
                                order_price=Decimal(15_000))
    try:
        broker.submit_limit_order(options)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


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

    options = TakeProfitOptions(amount=invalid_amount,
                                trigger_price=invalid_trigger,
                                order_price=invalid_limit)
    try:
        broker.submit_take_profit_order(OrderSide.SELL, options)
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

    options = TakeProfitOptions(amount=test_amount,
                                trigger_price=Decimal(12_000))
    try:
        broker.submit_take_profit_order(OrderSide.BUY, options)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised


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

    options = StopLossOptions(amount=invalid_amount,
                              trigger_price=invalid_trigger,
                              order_price=invalid_limit)
    try:
        broker.submit_stop_loss_order(OrderSide.SELL, options)
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

    options = StopLossOptions(amount=test_amount,
                              trigger_price=Decimal(8_000))
    try:
        broker.submit_stop_loss_order(OrderSide.BUY, options)
    except InsufficientFunds:
        insufficient_funds_raised = True
    assert insufficient_funds_raised
