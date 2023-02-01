from decimal import Decimal
from backintime.broker.default.broker import Broker
from backintime.broker.default.fees import FeesEstimator
from backintime.broker.base import (
    OrderSide, 
    MarketOrderOptions, 
    LimitOrderOptions, 
    TakeProfitOptions, 
    StopLossOptions,
    InvalidOrderData
)


def test_market_order_submission_with_invalid_amount():
    """Test market order submission with invalid value in `amount`."""
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_order_data_raised = False

    market_order = MarketOrderOptions(OrderSide.BUY, invalid_amount)
    try:
        broker.submit_market_order(market_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_market_order_submission_with_invalid_percentage_amount():
    """
    Test market order submission with invalid value
    in `percentage_amount`.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_order_data_raised = False

    market_order = MarketOrderOptions(OrderSide.BUY, 
                                      percentage_amount=invalid_amount)
    try:
        broker.submit_market_order(market_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_market_order_submission_without_amount():
    """Test market order submission with `None` in amount."""
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_order_data_raised = False

    market_order = MarketOrderOptions(OrderSide.BUY, None, None)
    try:
        broker.submit_market_order(market_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_invalid_market_order_submission():
    """
    Test market order submission with invalid values 
    in `amount` and `percentage_amount`.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_order_data_raised = False

    market_order = MarketOrderOptions(OrderSide.BUY, 
                                      amount=invalid_amount, 
                                      percentage_amount=invalid_amount)
    try:
        broker.submit_market_order(market_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_take_profit_order_submission_with_invalid_amount():
    """Test Take Profit submission with invalid value in `amount`."""
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    sample_limit = Decimal(15_000)
    sample_trigger = Decimal(12_000)
    invalid_order_data_raised = False

    tp = TakeProfitOptions(amount=invalid_amount,
                           trigger_price=sample_trigger,
                           order_price=sample_limit)
    try:
        broker.submit_take_profit_order(OrderSide.SELL, tp)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_take_profit_order_submission_with_invalid_percentage_amount():
    """
    Test Take Profit submission with invalid value 
    in `percentage_amount`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    sample_limit = Decimal(15_000)
    sample_trigger = Decimal(12_000)
    invalid_order_data_raised = False

    tp = TakeProfitOptions(percentage_amount=invalid_amount,
                           trigger_price=sample_trigger,
                           order_price=sample_limit)
    try:
        broker.submit_take_profit_order(OrderSide.SELL, tp)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_take_profit_order_submission_with_invalid_trigger_price():
    """
    Test Take Profit submission with invalid value 
    in `trigger_price`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = Decimal(10_000)
    sample_limit = Decimal(15_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    tp = TakeProfitOptions(amount=sample_amount,
                           trigger_price=invalid_trigger,
                           order_price=sample_limit)
    try:
        broker.submit_take_profit_order(OrderSide.SELL, tp)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_take_profit_order_submission_with_invalid_order_price():
    """
    Test Take Profit submission with invalid value 
    in `order_amount`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = Decimal(10_000)
    sample_trigger = Decimal(12_000)
    invalid_limit = Decimal(-15_000)
    invalid_order_data_raised = False

    tp = TakeProfitOptions(amount=sample_amount,
                           trigger_price=sample_trigger,
                           order_price=invalid_limit)
    try:
        broker.submit_take_profit_order(OrderSide.SELL, tp)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_invalid_take_profit_order_submission():
    """
    Check whether an attempt to submit invalid Take Profit
    (`amount`, `percentage_amount`, `trigger_price`, `order_price` <= 0) 
    will raise `InvalidOrderData`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_limit = Decimal(-15_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    tp = TakeProfitOptions(amount=invalid_amount,
                           percentage_amount=invalid_amount,
                           trigger_price=invalid_trigger,
                           order_price=invalid_limit)
    try:
        broker.submit_take_profit_order(OrderSide.SELL, tp)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_stop_loss_order_submission_with_invalid_amount():
    """Test Stop Loss submission with invalud value in `amount`."""
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    sample_limit = Decimal(15_000)
    sample_trigger = Decimal(12_000)
    invalid_order_data_raised = False

    stop_loss = StopLossOptions(amount=invalid_amount,
                                trigger_price=sample_trigger,
                                order_price=sample_limit)
    try:
        broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_stop_loss_order_submission_with_invalid_percentage_amount():
    """
    Test Stop Loss submission with invalud value
    in `percentage_amount`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    sample_limit = Decimal(15_000)
    sample_trigger = Decimal(12_000)
    invalid_order_data_raised = False

    stop_loss = StopLossOptions(percentage_amount=invalid_amount,
                                trigger_price=sample_trigger,
                                order_price=sample_limit)
    try:
        broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_stop_loss_order_submission_with_invalid_trigger_price():
    """
    Test Stop Loss submission with invalud value
    in `trigger_price`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = Decimal(10_000)
    sample_limit = Decimal(15_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    stop_loss = StopLossOptions(amount=sample_amount,
                                trigger_price=invalid_trigger,
                                order_price=sample_limit)
    try:
        broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_stop_loss_order_submission_with_invalid_order_price():
    """
    Test Stop Loss submission with invalud value
    in `order_price`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = Decimal(10_000)
    sample_trigger = Decimal(12_000)
    invalid_limit = Decimal(-15_000)
    invalid_order_data_raised = False

    stop_loss = StopLossOptions(amount=sample_amount,
                                trigger_price=sample_trigger,
                                order_price=invalid_limit)
    try:
        broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_invalid_stop_loss_order_submission():
    """
    Check whether an attempt to submit invalid Stop Loss
    (`amount`, `percentage_amount`, `trigger_price`, `order_price` <= 0) 
    will raise `InvalidOrderData`.
    """
    fees = FeesEstimator(Decimal('0'), Decimal('0'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_limit = Decimal(-15_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    stop_loss = StopLossOptions(amount=invalid_amount,
                                percentage_amount=invalid_amount,
                                trigger_price=invalid_trigger,
                                order_price=invalid_limit)
    try:
        broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_with_invalid_amount():
    """Test submission of Limit order with invalid value in `amount`.""" 
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    sample_limit = Decimal(15_000)
    invalid_order_data_raised = False

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    amount=invalid_amount)
    try:
        broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_with_invalid_percentage_amount():
    """
    Test submission of Limit order with invalid value 
    in `percentage_amount`.
    """ 
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    sample_limit = Decimal(15_000)
    invalid_order_data_raised = False

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    percentage_amount=invalid_amount)
    try:
        broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_without_amount():
    """Test submission of Limit order with `None` in `amount`.""" 
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(15_000)
    invalid_order_data_raised = False

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    amount=None,
                                    percentage_amount=None)
    try:
        broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_with_invalid_take_profit():
    """Test Limit order submission with invalid Take Profit."""
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(15_000)
    sample_amount = Decimal(10_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    invalid_tp = TakeProfitOptions(amount=sample_amount,
                                   trigger_price=invalid_trigger)

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    amount=sample_amount,
                                    take_profit=invalid_tp)
    try:
        broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_with_invalid_stop_loss():
    """Test Limit order submission with invalid Stop Loss."""
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(15_000)
    sample_amount = Decimal(10_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    invalid_sl = StopLossOptions(amount=sample_amount,
                                 trigger_price=invalid_trigger)

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    amount=sample_amount,
                                    stop_loss=invalid_sl)
    try:
        broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_limit_order_submission_with_invalid_tpsl():
    """
    Test Limit order submission with invalid 
    Take Profit and Stop Loss.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(15_000)
    sample_amount = Decimal(10_000)
    invalid_trigger = Decimal(-12_000)
    invalid_order_data_raised = False

    invalid_tp = TakeProfitOptions(amount=sample_amount,
                                   trigger_price=invalid_trigger)

    invalid_sl = StopLossOptions(amount=sample_amount,
                                 trigger_price=invalid_trigger)

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    amount=sample_amount,
                                    take_profit=invalid_tp,
                                    stop_loss=invalid_sl)
    try:
        broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised


def test_invalid_limit_order_submission():
    """
    Check whether an attempt to submit invalid Limit order
    (`amount`, `percentage_amount`, and `order_price` <= 0) 
    will raise `InvalidOrderData`.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    invalid_amount = Decimal(-10_000)
    invalid_limit = Decimal(-15_000)
    invalid_order_data_raised = False

    limit_order = LimitOrderOptions(OrderSide.BUY, invalid_limit, 
                                    invalid_amount, invalid_amount)
    try:
        broker.submit_limit_order(limit_order)
    except InvalidOrderData as e:
        invalid_order_data_raised = True
    assert invalid_order_data_raised
