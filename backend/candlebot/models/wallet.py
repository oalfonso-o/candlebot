import logging
from typing import List

from candlebot.models.position import Position

logger = logging.getLogger(__name__)


class Wallet:

    position_types = ['long', 'short']

    def __init__(
        self,
        balance_origin: float = 1000,
        amount_to_open: float = 100,
        percentage_to_close: float = 100,
        balance_long: float = 0,
        balance_short: float = 0,
        transaction_fee: float = 0.00075,
    ):
        self.balance_origin_start = balance_origin
        self.balance_origin = balance_origin
        self.amount_to_open = amount_to_open
        self.percentage_to_close = percentage_to_close
        self.balance_long = balance_long
        self.balance_short = balance_short
        self.transaction_fee = transaction_fee
        self.positions_long: List[Position] = []
        self.positions_short: List[Position] = []

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
        open_amount_w_fee = open_amount - (open_amount * self.transaction_fee)
        prev_open_balance = getattr(self, balance_type_fieldname)
        new_open_balance = prev_open_balance + open_amount_w_fee
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
        positions_type_fieldname = f'positions_{type_}'
        prev_positions = getattr(self, positions_type_fieldname)
        prev_positions.append(position)
        setattr(self, positions_type_fieldname, prev_positions)

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
        if prev_open_balance <= 0:
            logger.warning(
                f'Trying to close position with {percentage}% with an open '
                f'balance of {prev_open_balance}. Aborting close.'
            )
            return
        close_amount = prev_open_balance / 100 * percentage
        close_amount_w_fee = (
            close_amount - (close_amount * self.transaction_fee)
        )
        new_open_balance = prev_open_balance - close_amount
        setattr(self, balance_type_fieldname, new_open_balance)
        closed_amount_to_the_origin = close_amount_w_fee * price
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
        positions_type_fieldname = f'positions_{type_}'
        prev_positions = getattr(self, positions_type_fieldname)
        prev_positions.append(position)
        setattr(self, positions_type_fieldname, prev_positions)
