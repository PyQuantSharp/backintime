from decimal import Decimal
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


def test_market_order_cancellation():
    """Test cancellation of a valid market order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)
    options = MarketOrderOptions(test_side, test_amount)
    market_order = broker.submit_market_order(options)
    broker.cancel_order(market_order.order_id)

    available_fiat_balance = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    assert market_order.status is expected_status and \
            available_fiat_balance == expected_fiat and \
            fiat_balance == expected_fiat


def test_limit_order_cancellation():
    """Test cancellation of a limit order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)
    options = LimitOrderOptions(test_side, 
                                amount=test_amount, 
                                order_price=Decimal(15_000))
    limit_order = broker.submit_limit_order(options)
    broker.cancel_order(limit_order.order_id)

    available_fiat_balance = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    assert limit_order.status is expected_status and \
            available_fiat_balance == expected_fiat and \
            fiat_balance == expected_fiat


def test_take_profit_order_cancellation():
    """Test cancellation of a valid take profit order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)

    options = TakeProfitOptions(amount=test_amount,
                                trigger_price=Decimal(1_000),
                                order_price=Decimal(500))
    tp = broker.submit_take_profit_order(test_side, options)
    broker.cancel_order(tp.order_id)

    available_fiat_balance = broker.balance.available_fiat_balance
    fiat_balance = broker.balance.fiat_balance
    assert tp.status is expected_status and \
            available_fiat_balance == expected_fiat and \
            fiat_balance == expected_fiat


def test_stop_loss_order_cancellation():
    """Test cancellation of a valid stop loss order."""
    test_side = OrderSide.BUY
    test_amount = Decimal(5_000)
    test_balance = Decimal(10_000)
    expected_status = OrderStatus.CANCELLED
    expected_fiat = test_balance

    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(test_balance, fees)

    options = StopLossOptions(amount=test_amount,
                              trigger_price=Decimal(1_000),
                              order_price=Decimal(500))
    sl = broker.submit_stop_loss_order(test_side, options)
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

    options = MarketOrderOptions(OrderSide.BUY, Decimal(10_000))
    market_order = broker.submit_market_order(options)
    broker.cancel_order(market_order.order_id)

    try:
        broker.cancel_order(market_order.order_id)
    except OrderCancellationError:
        order_cancellation_error_raised = True
    assert order_cancellation_error_raised
