from typing import Iterable
from ..broker.trade import Trade

import pandas as pd
import csv


class BacktestingResults:

    __stat_keys = [
        'duration',
        'positions',
        'profit',
        'best_deal',
        'best_deal, %',
        'worst_deal',
        'worst_deal, %',
        'win_rate',
        'average_profit, %',
        'average_loss, %',
        'profitable_positions',
        'total_trades'
    ]

    def __init__(self, positions, start_date, end_date, presicion=2):
        self._positions = positions
        self._trades = None  # to use dataframe' .to_csv method
        self._stat = dict.fromkeys(self.__stat_keys, 0)
        self._stat['duration'] = end_date - start_date
        
        all_profit = 0
        all_losses = 0

        for pos in positions:
            profit = pos.profit
            profit_ratio = pos.profit_ratio

            self._stat['profit'] += profit
            if profit > 0:
                self._stat['profitable_positions'] += 1
                all_profit += profit_ratio
            if profit < 0:
                all_losses += profit_ratio
            if profit > self._stat['best_deal']:
                self._stat['best_deal'] = profit
            if profit < self._stat['worst_deal']:
                self._stat['worst_deal'] = profit
            if profit_ratio > self._stat['best_deal, %']:
                self._stat['best_deal, %'] = profit_ratio
            if profit_ratio < self._stat['worst_deal, %']:
                self._stat['worst_deal, %'] = profit_ratio

            self._stat['total_trades'] += len(pos._trades)
            self._stat['positions'] += 1

        profitable = self._stat['profitable_positions']
        total = self._stat['positions']
        if total:
            self._stat['win_rate'] = (profitable / total)*100
            self._stat['average_profit, %'] = all_profit/profitable
            self._stat['average_loss, %'] = all_losses/(total - profitable)
        self.__round_values(self._stat, presicion)

    def to_csv(self, filename: str, sep=',', summary=True) -> None:
        """Dump the trades history to a csv file

        :param filename:
            name of the file in current directory
            (will be created if not exists)
        :param sep:
            columns separator
        :param summary:
            if True (by default), statistics summary will be included
                in dump before the list of trades
        """
        if summary:
            self._write_summary(filename, sep)
        if not self._trades:
            self._trades = pd.DataFrame(columns=[
                'time_1',
                'time_2',
                'type',
                'side',
                'notional',
                'price',
                'quantity',
                'profit',
                'fee'
            ])

            for pos in self._positions:
                for trade in pos.trades():
                    trade = self._trade_to_dict(trade)
                    self._trades = self._trades.append(trade, ignore_index=True)
        self._trades.to_csv(filename, sep, mode='a')

    def _write_summary(self, filename: str, sep=','):
        with open(filename, 'a') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self._stat.keys(),
                delimiter=sep,
                lineterminator='\n'
            )
            writer.writeheader()
            writer.writerows([self._stat])
            csvfile.write('\n')

    @staticmethod
    def __round_values(data, precision):
        for k, v in data.items():
            if isinstance(v, float):
                data[k] = round(v, precision)

    @staticmethod
    def _trade_to_dict(trade):
        order = trade.order
        return {
            'time_1': trade.time_1,
            'time_2': trade.time_2,
            'type': order.type.name,
            'side': order.side,
            'notional': round(order.notional, 2),
            'price': round(order.price, 2),
            'quantity': round(order.quantity, 2),
            'profit': round(trade.profit, 2),
            'fee': round(trade.fee, 2)
        }

    def __getattr__(self, attr):
        return self._stat.get(attr)

    def __repr__(self):
        return '\n'.join([
            f'{k}: {v}'
                for k, v in self._stat.items()
        ])
