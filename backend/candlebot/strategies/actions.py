import abc


class PostOpenActions(metaclass=abc.ABCMeta):
    """Contains actions to do after opening position, like setting stop loss"""

    def post_open_set_zigzag_stop_loss(self, crow):
        for qrow in self.queue:
            if qrow['zigzag'] and qrow['zigzag'] < crow['low']:
                self.stop_loss = qrow['zigzag']
                return
        self.stop_loss = crow['close'] - (crow['close'] / 100)
        # raise Exception('Lower zigzag not found, no stop loss could be set')

    def remove_stop_loss(self, crow):
        self.stop_loss = 0

    def remove_last_open_pos_close_value(self, crow):
        self.last_open_pos_close_value = 0
