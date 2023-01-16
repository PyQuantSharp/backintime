import typing as t
from decimal import Decimal
from datetime import datetime
from itertools import zip_longest
from pytest import fixture
from backintime.timeframes import Timeframes as tf
from backintime.broker.broker import Trade, OrderInfo
from backintime.broker.orders import (
    Order,
    OrderSide,
    OrderType,
)
from backintime.result.stats import (
    get_stats,
    Stats,
    TradeProfit,
    _fifo_profit, 
    _lifo_profit, 
    _avco_profit,
    UnexpectedProfitLossAlgorithm
)


@fixture
def sample_trades() -> t.List[Trade]:
    orders = [
        Order(side=OrderSide.BUY,
              order_type=OrderType.LIMIT,
              amount=Decimal(40_000),
              date_created=None,
              order_price=Decimal(40_000)),

        Order(side=OrderSide.BUY,
              order_type=OrderType.LIMIT,
              amount=Decimal(50_000),
              date_created=None,
              order_price=Decimal(50_000)),

        Order(side=OrderSide.SELL,
              order_type=OrderType.LIMIT,
              amount=Decimal(1),
              date_created=None,
              order_price=Decimal(45_000)),

        Order(side=OrderSide.SELL,
              order_type=OrderType.LIMIT,
              amount=Decimal(1),
              date_created=None,
              order_price=Decimal(65_000))
    ]

    for order in orders:
        order.fill_price = order.order_price
        order.trading_fee = Decimal(0)

    trades = [
        Trade(trade_id=order_id,
              result_balance=None,
              order_info=OrderInfo(order_id, order))
                    for order_id, order in enumerate(orders)
    ]
    return trades


def test_fifo_profit_loss(sample_trades):
    """Test FIFO Profit/Loss calculation."""
    expected_profit = [
        TradeProfit(trade_id=2, order_id=2,
                    relative_profit=Decimal('12.5'),
                    absolute_profit=Decimal(5_000)),
        TradeProfit(trade_id=3, order_id=3,
                    relative_profit=Decimal('30'),
                    absolute_profit=Decimal(15_000))
    ]

    trades_profit = _fifo_profit(sample_trades)
    for estimated, expected in zip_longest(trades_profit, expected_profit):
        assert estimated is not None
        assert estimated.trade_id == expected.trade_id
        assert estimated.order_id == expected.order_id
        assert estimated.absolute_profit == expected.absolute_profit
        assert estimated.relative_profit == expected.relative_profit


def test_fifo_profit_loss_empty_trades():
    """Test FIFO Profit/Loss calculation with empty trades."""
    exception_raised = False
    result = None

    try:
        result = _fifo_profit([])
    except:
        exception_raised = True
    assert not exception_raised and \
            not result is None and len(result) == 0


def test_lifo_profit_loss(sample_trades):
    """Test LIFO Profit/Loss calculation."""
    expected_profit = [
        TradeProfit(trade_id=2, order_id=2,
                    relative_profit=Decimal('-10'),
                    absolute_profit=Decimal(-5_000)),
        TradeProfit(trade_id=3, order_id=3,
                    relative_profit=Decimal('62.5'),
                    absolute_profit=Decimal(25_000))
    ]

    trades_profit = _lifo_profit(sample_trades)
    for estimated, expected in zip_longest(trades_profit, expected_profit):
        assert estimated is not None
        assert estimated.trade_id == expected.trade_id
        assert estimated.order_id == expected.order_id
        assert estimated.absolute_profit == expected.absolute_profit
        assert estimated.relative_profit == expected.relative_profit


def test_lifo_profit_loss_empty_trades():
    """Test LIFO Profit/Loss calculation with empty trades."""
    exception_raised = False
    result = None

    try:
        result = _lifo_profit([])
    except:
        exception_raised = True
    assert not exception_raised and \
            not result is None and len(result) == 0


def test_avco_profit_loss(sample_trades):
    """Test AVCO Profit/Loss calculation."""
    expected_profit = [
        TradeProfit(trade_id=2, order_id=2,
                    relative_profit=Decimal('0'),
                    absolute_profit=Decimal(0)),
        TradeProfit(trade_id=3, order_id=3,
                    relative_profit=Decimal('44.44'),
                    absolute_profit=Decimal(20_000))
    ]

    trades_profit = _avco_profit(sample_trades)
    for estimated, expected in zip_longest(trades_profit, expected_profit):
        assert estimated is not None
        assert estimated.trade_id == expected.trade_id
        assert estimated.order_id == expected.order_id
        assert estimated.absolute_profit == expected.absolute_profit
        estimated_relative = round(estimated.relative_profit)
        expected_relative = round(expected.relative_profit)
        assert estimated_relative == expected_relative


def test_avco_profit_loss_empty_trades():
    """Test AVCO Profit/Loss calculation with empty trades."""
    exception_raised = False
    result = None

    try:
        result = _acvo_profit([])
    except:
        exception_raised = True
    assert not exception_raised and \
            not result is None and len(result) == 0


def test_unexpected_algorithm_will_raise():
    """
    Check whether passing unexpected algorithm to `get_stats` 
    will raise `UnexpectedProfitLossAlgorithm`.
    """
    wrong_algorithm = 'RANDOM'
    unexpected_algorithm_raised = False

    try:
        get_stats(wrong_algorithm, [])
    except UnexpectedProfitLossAlgorithm:
        unexpected_algorithm_raised = True    
    assert unexpected_algorithm_raised


def test_stats_empty_trades():
    """
    Test `get_stats` with empty trades. 
    Expect not None, valid `Stats` object as a result.
    """
    result: t.Optional[Stats] = None
    exception_raised = False

    try:
        result = get_stats('FIFO', [])
    except:
        exception_raised = True
    finally:
        assert not exception_raised and \
            not result is None and isinstance(result, Stats)  
