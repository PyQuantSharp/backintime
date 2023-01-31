from decimal import Decimal
from backintime.broker.default.fees import FeesEstimator
from backintime.broker.default.broker import Broker 
from backintime.broker.base import (
    OrderSide, 
    MarketOrderOptions, 
    LimitOrderOptions,
    TakeProfitOptions,
    StopLossOptions
)


def test_balance_after_market_buy_submission_with_absolute_amount():
    """
    Ensure that balance properly decreases after Market BUY submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = Decimal('9950.24')
    expected_balance = Decimal('0.01')

    market_order = MarketOrderOptions(OrderSide.BUY, sample_amount)
    broker.submit_market_order(market_order)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_market_buy_submission_with_percentage_amount():
    """
    Ensure that balance properly decreases after Market BUY submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_fiat_balance / 2

    market_order = MarketOrderOptions(OrderSide.BUY, 
                                      percentage_amount=sample_amount)
    broker.submit_market_order(market_order)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_market_buy_submission_with_max_fiat():
    """
    Ensure that balance properly decreases after Market BUY submission
    with max available fiat.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    market_order = MarketOrderOptions(OrderSide.BUY, sample_amount)
    broker.submit_market_order(market_order)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_market_sell_submission_with_absolute_amount():
    """
    Ensure that balance properly decreases after Market SELL submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_amount = Decimal(10)
    expected_balance = Decimal(0)

    market_order = MarketOrderOptions(OrderSide.SELL, sample_amount)
    broker.submit_market_order(market_order)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_market_sell_submission_with_percentage_amount():
    """
    Ensure that balance properly decreases after Market SELL submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_crypto_balance / 2

    market_order = MarketOrderOptions(OrderSide.SELL, 
                                      percentage_amount=sample_amount)
    market_order = broker.submit_market_order(market_order)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_market_sell_submission_with_max_crypto():
    """
    Ensure that balance properly decreases after Market SELL submission
    with max available crypto.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(0)

    market_order = MarketOrderOptions(OrderSide.SELL, sample_amount)
    broker.submit_market_order(market_order)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_limit_buy_submission_with_absolute_amount():
    """
    Ensure that balance properly decreases after Limit BUY submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(12_000)
    sample_amount = Decimal('9950.24')
    expected_balance = Decimal('0.01')

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    amount=sample_amount)
    broker.submit_limit_order(limit_order)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_limit_buy_submission_with_percentage_amount():
    """
    Ensure that balance properly decreases after Limit BUY submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(12_000)
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_fiat_balance / 2

    limit_order = LimitOrderOptions(OrderSide.BUY,
                                    order_price=sample_limit,
                                    percentage_amount=sample_amount)
    broker.submit_limit_order(limit_order)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_limit_buy_submission_with_max_fiat():
    """
    Ensure that balance properly decreases after Limit BUY submission
    with max available fiat.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(12_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    limit_order = LimitOrderOptions(OrderSide.BUY, 
                                    order_price=sample_limit, 
                                    amount=sample_amount)
    broker.submit_limit_order(limit_order)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_limit_sell_submission_with_absolute_amount():
    """
    Ensure that balance properly decreases after Limit SELL submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_limit = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(0)

    limit_order = LimitOrderOptions(OrderSide.SELL, 
                                    order_price=sample_limit, 
                                    amount=sample_amount)
    broker.submit_limit_order(limit_order)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_limit_sell_submission_with_percentage_amount():
    """
    Ensure that balance properly decreases after Limit SELL submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_limit = Decimal(12_000)
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_crypto_balance / 2

    limit_order = LimitOrderOptions(OrderSide.SELL,
                                    order_price=sample_limit,
                                    percentage_amount=sample_amount)
    broker.submit_limit_order(limit_order)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_limit_sell_submission_with_max_crypto():
    """
    Ensure that balance properly decreases after Limit SELL submission
    with max available crypto.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_limit = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    limit_order = LimitOrderOptions(OrderSide.SELL, 
                                    order_price=sample_limit, 
                                    amount=sample_amount)
    broker.submit_limit_order(limit_order)

    result_balance = broker.balance.available_crypto_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_taker_profit_buy_with_absolute_amount():
    """
    Ensure that balance properly decreases after Take Profit BUY submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = Decimal('9950.24')
    expected_balance = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_trigger, 
                                    amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.BUY, take_profit)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_taker_profit_buy_with_percentage_amount():
    """
    Ensure that balance properly decreases after Take Profit BUY submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_fiat_balance / 2

    take_profit = TakeProfitOptions(trigger_price=sample_trigger, 
                                    percentage_amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.BUY, take_profit)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_taker_profit_buy_with_max_fiat():
    """
    Ensure that balance properly decreases after Take Profit BUY submission
    with max available fiat.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_trigger, 
                                    amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.BUY, take_profit)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_take_profit_sell_submission_with_absolute_amount():
    """
    Ensure that balance properly decreases after Take Profit SELL submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(0)

    take_profit = TakeProfitOptions(trigger_price=sample_trigger, 
                                    amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.SELL, take_profit)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_take_profit_sell_submission_with_percentage_amount():
    """
    Ensure that balance properly decreases after Take Profit SELL submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_crypto_balance / 2

    take_profit = TakeProfitOptions(trigger_price=sample_trigger, 
                                    percentage_amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.SELL, take_profit)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance
 

def test_balance_after_taker_profit_sell_with_max_crypto():
    """
    Ensure that balance properly decreases after Take Profit SELL submission
    with max available crypto.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_trigger, 
                                    amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.SELL, take_profit)

    result_balance = broker.balance.available_crypto_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_stop_loss_buy_with_absolute_amount():
    """
    Ensure that balance properly decreases after Stop Loss BUY submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = Decimal('9950.24')
    expected_balance = Decimal('0.01')

    stop_loss = StopLossOptions(trigger_price=sample_trigger, 
                                amount=sample_amount)
    broker.submit_stop_loss_order(OrderSide.BUY, stop_loss)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_stop_loss_buy_with_percentage_amount():
    """
    Ensure that balance properly decreases after Stop Loss BUY submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_fiat_balance / 2

    stop_loss = StopLossOptions(trigger_price=sample_trigger, 
                                percentage_amount=sample_amount)
    broker.submit_stop_loss_order(OrderSide.BUY, stop_loss)
    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_stop_loss_buy_with_max_fiat():
    """
    Ensure that balance properly decreases after Stop Loss BUY submission
    with max available fiat.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    stop_loss = StopLossOptions(trigger_price=sample_trigger, 
                                amount=sample_amount)
    broker.submit_stop_loss_order(OrderSide.BUY, stop_loss)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_stop_loss_sell_submission_with_absolute_amount():
    """
    Ensure that balance properly decreases after Stop Loss SELL submission
    with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(0)

    stop_loss = StopLossOptions(trigger_price=sample_trigger, 
                                amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.SELL, stop_loss)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_stop_loss_sell_submission_with_percentage_amount():
    """
    Ensure that balance properly decreases after Stop Loss SELL submission
    with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = Decimal('50.00')    # 50%
    expected_balance = broker.balance.available_crypto_balance / 2

    stop_loss = StopLossOptions(trigger_price=sample_trigger, 
                                percentage_amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.SELL, stop_loss)
    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance
 

def test_balance_after_stop_loss_sell_with_max_crypto():
    """
    Ensure that balance properly decreases after Stop Loss SELL submission
    with max available crypto.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    stop_loss = StopLossOptions(trigger_price=sample_trigger, 
                                amount=sample_amount)
    broker.submit_take_profit_order(OrderSide.SELL, stop_loss)

    result_balance = broker.balance.available_crypto_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_tpsl_buy_submission_with_absolute_amount():
    """
    Ensure that balance properly decreases after Take Profit BUY 
    and Stop Loss BUY submission with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = Decimal('9950.24')
    expected_balance = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_tp_trigger, 
                                    amount=sample_amount)

    stop_loss = StopLossOptions(trigger_price=sample_sl_trigger, 
                                amount=sample_amount)

    broker.submit_take_profit_order(OrderSide.BUY, take_profit)
    broker.submit_stop_loss_order(OrderSide.BUY, stop_loss)

    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_tpsl_buy_submission_with_percentage_amount():
    """
    Ensure that balance properly decreases after Take Profit BUY 
    and Stop Loss BUY submission with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = Decimal('100.00')   # 100%
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_tp_trigger, 
                                    percentage_amount=sample_amount)

    stop_loss = StopLossOptions(trigger_price=sample_sl_trigger, 
                                percentage_amount=sample_amount)

    broker.submit_take_profit_order(OrderSide.BUY, take_profit)
    broker.submit_stop_loss_order(OrderSide.BUY, stop_loss)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_tpsl_buy_submission_with_max_fiat():
    """
    Ensure that balance properly decreases after Take Profit BUY 
    and Stop Loss BUY submission with max available fiat.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_tp_trigger, 
                                    amount=sample_amount)

    stop_loss = StopLossOptions(trigger_price=sample_sl_trigger, 
                                amount=sample_amount)

    broker.submit_take_profit_order(OrderSide.BUY, take_profit)
    broker.submit_stop_loss_order(OrderSide.BUY, stop_loss)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_tpsl_sell_with_absolute_amount():
    """
    Ensure that balance properly decreases after Take Profit SELL
    and Stop Loss SELL submission with absolute value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_tp_trigger, 
                                    amount=sample_amount)

    stop_loss = StopLossOptions(trigger_price=sample_sl_trigger, 
                                amount=sample_amount)

    broker.submit_take_profit_order(OrderSide.SELL, take_profit)
    broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)

    result_balance = broker.balance.available_crypto_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_tpsl_sell_with_percentage_amount():
    """
    Ensure that balance properly decreases after Take Profit SELL
    and Stop Loss SELL submission with percentage value in amount.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = Decimal('100.00')   # 100%
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_tp_trigger, 
                                    percentage_amount=sample_amount)

    stop_loss = StopLossOptions(trigger_price=sample_sl_trigger, 
                                percentage_amount=sample_amount)

    broker.submit_take_profit_order(OrderSide.SELL, take_profit)
    broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)

    result_balance = broker.balance.available_crypto_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_tpsl_sell_with_max_crypto():
    """
    Ensure that balance properly decreases after Take Profit SELL
    and Stop Loss SELL submission with max available crypto.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal('0.00')
    expected_deviation = Decimal('0.01')

    take_profit = TakeProfitOptions(trigger_price=sample_tp_trigger, 
                                    amount=sample_amount)

    stop_loss = StopLossOptions(trigger_price=sample_sl_trigger, 
                                amount=sample_amount)

    broker.submit_take_profit_order(OrderSide.SELL, take_profit)
    broker.submit_stop_loss_order(OrderSide.SELL, stop_loss)

    result_balance = broker.balance.available_crypto_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance or \
            result_deviation <= expected_deviation


def test_balance_after_market_buy_cancellation():
    """
    Ensure that balance is properly restored after 
    Market BUY cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal(10_000)

    options = MarketOrderOptions(OrderSide.BUY, sample_amount)
    market_order = broker.submit_market_order(options)
    broker.cancel_order(market_order.order_id)

    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_market_sell_cancellation():
    """
    Ensure that balance is properly restored after 
    Market SELL cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(10)

    options = MarketOrderOptions(OrderSide.SELL, sample_amount)
    market_order = broker.submit_market_order(options)
    broker.cancel_order(market_order.order_id)

    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_limit_buy_cancellation():
    """
    Ensure that balance is properly restored after 
    Limit BUY cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_limit = Decimal(12_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal(10_000)

    options = LimitOrderOptions(OrderSide.BUY, sample_limit, sample_amount)
    limit_order = broker.submit_limit_order(options)
    broker.cancel_order(limit_order.order_id)

    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_limit_sell_cancellation():
    """
    Ensure that balance is properly restored after 
    Limit SELL cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.release_crypto(Decimal(10))
    #
    sample_limit = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(10)

    options = LimitOrderOptions(OrderSide.SELL, sample_limit, sample_amount)
    limit_order = broker.submit_limit_order(options)
    broker.cancel_order(limit_order.order_id)

    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_take_profit_buy_cancellation():
    """
    Ensure that balance is properly restored after 
    Take Profit BUY cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal(10000)
    #expected_deviation = Decimal('0.01')

    options = TakeProfitOptions(trigger_price=sample_trigger, 
                                amount=sample_amount)
    take_profit = broker.submit_take_profit_order(OrderSide.BUY, options)
    broker.cancel_order(take_profit.order_id)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance # or \
    #        result_deviation <= expected_deviation


def test_balance_after_take_profit_sell_cancellation():
    """
    Ensure that balance is properly restored after 
    Take Profit SELL cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    #
    broker._balance.deposit_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(10)

    options = TakeProfitOptions(trigger_price=sample_trigger, 
                                amount=sample_amount)
    take_profit = broker.submit_take_profit_order(OrderSide.SELL, options)
    broker.cancel_order(take_profit.order_id)

    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_stop_loss_buy_cancellation():
    """
    Ensure that balance is properly restored after 
    Stop Loss BUY cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_trigger = Decimal(12_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal(10000)

    options = StopLossOptions(trigger_price=sample_trigger, 
                              amount=sample_amount)
    stop_loss = broker.submit_stop_loss_order(OrderSide.BUY, options)
    broker.cancel_order(stop_loss.order_id)

    result_balance = broker.balance.available_fiat_balance
    result_deviation = result_balance - expected_balance
    assert result_balance == expected_balance


def test_balance_after_stop_loss_sell_cancellation():
    """
    Ensure that balance is properly restored after 
    Stop Loss SELL cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    #
    broker._balance.deposit_crypto(Decimal(10))
    #
    sample_trigger = Decimal(12_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(10)

    options = StopLossOptions(trigger_price=sample_trigger, 
                              amount=sample_amount)
    stop_loss = broker.submit_stop_loss_order(OrderSide.SELL, options)
    broker.cancel_order(stop_loss.order_id)

    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance


def test_balance_after_tpsl_buy_cancellation():
    """
    Ensure that balance is properly restored after 
    Take Profit BUY and Stop Loss BUY cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = broker.max_fiat_for_taker
    expected_balance = Decimal(10000)

    tp_options = TakeProfitOptions(trigger_price=sample_tp_trigger,
                                   amount=sample_amount)

    sl_options = StopLossOptions(trigger_price=sample_sl_trigger, 
                                 amount=sample_amount)

    take_profit = broker.submit_take_profit_order(OrderSide.BUY, tp_options)
    stop_loss = broker.submit_stop_loss_order(OrderSide.BUY, sl_options)
    broker.cancel_order(stop_loss.order_id)
    broker.cancel_order(take_profit.order_id)

    result_balance = broker.balance.available_fiat_balance
    assert result_balance == expected_balance


def test_balance_after_tpsl_sell_cancellation():
    """
    Ensure that balance is properly restored after 
    Take Profit SELL and Stop Loss SELL cancellation.
    """
    fees = FeesEstimator(Decimal('0.005'), Decimal('0.005'))
    broker = Broker(Decimal(10_000), fees)
    # Add crypto
    broker._balance.deposit_crypto(Decimal(10))
    #
    sample_tp_trigger = Decimal(12_000)
    sample_sl_trigger = Decimal(8_000)
    sample_amount = broker.balance.available_crypto_balance
    expected_balance = Decimal(10)

    tp_options = TakeProfitOptions(trigger_price=sample_tp_trigger,
                                   amount=sample_amount)

    sl_options = StopLossOptions(trigger_price=sample_sl_trigger, 
                                 amount=sample_amount)

    take_profit = broker.submit_take_profit_order(OrderSide.BUY, tp_options)
    stop_loss = broker.submit_stop_loss_order(OrderSide.BUY, sl_options)
    broker.cancel_order(stop_loss.order_id)
    broker.cancel_order(take_profit.order_id)

    result_balance = broker.balance.available_crypto_balance
    assert result_balance == expected_balance