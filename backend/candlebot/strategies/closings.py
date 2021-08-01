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
        self.losses += 1
        logging.info(f'LOSE close because {reason}')
        return prev_stop_loss

    def close_win_generic(self, crow, reason):
        win_desired = (
            self.last_open_pos_close_value
            + (self.last_open_pos_close_value / 100 * constants.FEE_PERCENT)
        )
        if crow['close'] < win_desired:
            self.losses += 1
            logging.info(f'LOSE close because {reason}')
            return crow['close']
        elif crow['close'] >= win_desired:
            self.wins += 1
            logging.info(f'WIN close because {reason}')
            return crow['close']
