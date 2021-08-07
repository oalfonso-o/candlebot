import abc
import logging

from candlebot.strategies import constants


class Closings(metaclass=abc.ABCMeta):
    """Contains methods to close position

    This class must be inherited from an Strategy.
    When closing a position there are few things to do, account the loss/win,
    log, reseting some values. To avoid writing the same logic in diferent
    strategies this class includes these methods.
    """

    def close_lose_by_stop_loss(self, crow, reason):
        prev_stop_loss = self.stop_loss
        self.stop_loss = 0
        self.wallet.stats.losses += 1
        logging.info(f'LOSE: {reason}')
        return prev_stop_loss

    def close_win_generic(self, crow, reason):
        win_desired = (
            self.last_open_pos_close_value
            + (self.last_open_pos_close_value / 100 * constants.FEE_PERCENT)
        )
        self.stop_loss = 0
        if crow['close'] < win_desired:
            self.wallet.stats.losses += 1
            logging.info(f'LOSE: {reason}')
            return crow['close']
        elif crow['close'] >= win_desired:
            self.wallet.stats.wins += 1
            logging.info(f'WIN: {reason}')
            return crow['close']

    def close_win_pip_margin(self, crow, reason):
        last_open_value_pips = self.last_open_pos_close_value / self.pips_total
        high_diff = last_open_value_pips * self.win_pips_margin
        close_pos = self.last_open_pos_close_value + high_diff
        self.stop_loss = 0
        self.wallet.stats.wins += 1
        logging.info(f'WIN: {reason}')
        return close_pos

    def close_lose_pip_margin(self, crow, reason):
        last_open_value_pips = self.last_open_pos_close_value / self.pips_total
        low_diff = last_open_value_pips * self.loss_pips_margin
        close_pos = self.last_open_pos_close_value - low_diff
        self.stop_loss = 0
        self.wallet.stats.losses += 1
        logging.info(f'LOSE: {reason}')
        return close_pos
