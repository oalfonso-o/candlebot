from typing import List

from candlebot.models.position import Position


class Wallet:

    position_types = ['long', 'short']

    def __init__(
        self,
        balance_origin: float = 1000,
        amount_to_open: float = 100,
        percentage_to_close: float = 100,
        balance_long: float = 0,
        balance_short: float = 0,
    ):
        self.balance_origin = balance_origin
        self.amount_to_open = amount_to_open
        self.percentage_to_close = percentage_to_close
        self.balance_long = balance_long
        self.balance_short = balance_short
        self.positions: List[Position] = []

    def open_pos(
        self,
        type_: str,
        price: float,
        timestamp: int,
        amount_to_open: float = 0,
    ):
        if not amount_to_open:
            amount_to_open = self.amount_to_open
        if type_ not in self.position_types:
            raise ValueError(f'Type {type_} not in {self.position_types}')
        balance_type_fieldname = f'balance_{type_}'
        open_amount = amount_to_open / price
        prev_open_balance = getattr(self, balance_type_fieldname)
        new_open_balance = prev_open_balance + open_amount
        setattr(self, balance_type_fieldname, new_open_balance)
        self.balance_origin -= amount_to_open
        position = Position(
            type_=type_,
            action='open',
            price=price,
            timestamp=timestamp,
            amount=amount_to_open,
            balance_origin=self.balance_origin,
            balance_long=self.balance_long,
            balance_short=self.balance_short,
        )
        self.positions.append(position)
        return position

    def close_pos(
        self,
        type_: str,
        price: float,
        timestamp: int,
        percentage: float = 0,
    ):
        if not percentage:
            percentage = self.percentage_to_close
        if type_ not in self.position_types:
            raise ValueError(f'Type {type_} not in {self.position_types}')
        balance_type_fieldname = f'balance_{type_}'
        prev_open_balance = getattr(self, balance_type_fieldname)
        close_amount = prev_open_balance / 100 * percentage
        new_open_balance = prev_open_balance - close_amount
        setattr(self, balance_type_fieldname, new_open_balance)
        closed_amount_to_the_origin = close_amount * price
        self.balance_origin += closed_amount_to_the_origin
        position = Position(
            type_=type_,
            action='close',
            price=price,
            timestamp=timestamp,
            amount=closed_amount_to_the_origin,
            balance_origin=self.balance_origin,
            balance_long=self.balance_long,
            balance_short=self.balance_short,
        )
        self.positions.append(position)
        return position

    def chart_data(self):
        data = {
            'balance_origin': [],
            'balance_long': [],
            'balance_short': [],
            'open_positions': [],
            'close_positions': [],
        }
        for p in self.positions:
            t = p.timestamp
            data['balance_origin'].append(
                {'time': t, 'value': p.balance_origin})
            data['balance_long'].append(
                {'time': t, 'value': p.balance_long})
            data['balance_short'].append(
                {'time': t, 'value': p.balance_short})
            data[f'{p.action}_positions'].append(
                {'time': t, 'value': p.price})
        return data
