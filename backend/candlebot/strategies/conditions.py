import abc
import itertools
import operator

from candlebot.strategies import constants

OPS = {
    'gt': operator.gt,
    'ls': operator.lt,
}


def generate_generic_trend_conditions():
    candles = ['crow', 'ago_1', 'ago_2', 'ago_3', 'ago_4', 'ago_5']
    candle_parts = ['low', 'close', 'open', 'high']
    smmas = ['smma21', 'smma50', 'smma200']
    conds = ['gt', 'ls']
    # DEFINE METHODS FOR CANDLES
    product = itertools.product(candles, candle_parts, smmas, conds)
    for candle, candle_part, smma, cond in product:
        candle_str = candle
        if candle == 'crow':
            candle = candle
        elif 'ago' in candle:
            days_ago = candle.split('_')[1]
            queue_index = int(days_ago) - 1
            candle = f'self.queue[{queue_index}]'
        name = f'{candle_str}_{candle_part}_{cond}_{smma}'
        method_str = f'def {name}(self, crow):op = OPS["{cond}"];return op({candle}["{candle_part}"], crow["{smma}"])'  # noqa
        exec(method_str, globals())
        setattr(TrendConditionsMixin, name, globals()[name])
    # DEFINE METHODS FOR ALL QUEUE CANDLES
    product = itertools.product(candle_parts, smmas, conds)
    for candle_part, smma, cond in product:
        name = f'all_queue_{candle_part}_{cond}_{smma}'
        method_str = f'def {name}(self, crow):op = OPS["{cond}"];return all([op(c["{candle_part}"], c["{smma}"]) for c in self.queue])'  # noqa
        exec(method_str, globals())
        setattr(TrendConditionsMixin, name, globals()[name])


class TrendConditionsMixin(metaclass=abc.ABCMeta):
    """Component of Conditions class with only trend conditions

    As all these trend conditions are permutations of:
    - candle: actual, 1 day ago, 2, 3, etc
    - part of the candle: open, close, high, low
    - condition: >, <
    - smma: 21, 50, 200
    There's a method `generate_generic_trend_conditions` that generates these
    methods automatically.
    Ideally this can be done with parameters but the idea is to keep all
    methods with the same input (crow) and same output (True/False)
    """

    def trend_long(self, crow):
        return bool(self.direction == 1)


generate_generic_trend_conditions()


class Conditions(TrendConditionsMixin, metaclass=abc.ABCMeta):
    """Contains methods with default conditions to be used by strategies

    Strategies con combine these conditions to create their custom strategies.
    All the returns are always a boolean value.
    All methods are instance methods and recieve the current row being
    processed.

    We have to distinguish between:
        - 'crow': current row, received as argument
        - 'prow': previous row, retrieved from self.queue
    """

    def there_is_not_an_open_position(self, crow):
        return bool(not self.last_open_pos_close_value)

    def circular_queue_is_full(self, crow):
        return len(self.queue) == self.len_queue

    def any_prev_rows_have_been_StochRSI_oversold_0_05(self, crow):
        for qrow in self.queue:
            if qrow['stoch_rsi_k'] < 0.05:
                return True
        return False

    def all_5_prev_rows_were_not_touching_smma21(self, crow):
        for qrow in self.queue[:5]:
            if qrow['low'] < qrow['smma21']:
                return False

    def last_fractal_candle_in_last_5_prev_rows_was_not_bear(self, crow):
        for qrow in self.queue[:5]:
            if qrow['william_bear_fractals']:
                return False
            if qrow['william_bull_fractals']:
                return True
        return True

    def bull_fractal(self, crow):
        """Fractals need two previous candles to be calculated"""
        return bool(self.queue[1]['william_bull_fractals'])

    def bull_engulfing(self, crow):
        return bool(constants.FULL_BULL_ENGULFING in crow['tags'])

    def rsi_k_crow_lt_10(self, crow):
        return bool(crow['stoch_rsi_k'] < 0.10)

    def rsi_k_crow_gt_rsi_d_crow(self, crow):
        return bool(crow['stoch_rsi_k'] > crow['stoch_rsi_d'])

    def rsi_k_crow_is_0(self, crow):
        return bool(crow['stoch_rsi_k'] == 0)

    def all_3_prev_rows_rsi_k_increasing(self, crow):
        return bool(
            crow['stoch_rsi_k']
            >= self.queue[0]['stoch_rsi_k']
            >= self.queue[1]['stoch_rsi_k']
        )

    def crow_green(self, crow):
        return bool(crow['color'] == 'green')

    def crow_red(self, crow):
        return bool(crow['color'] == 'red')

    def crow_doji(self, crow):
        return bool(constants.DOJI in crow['tags'])

    def crow_not_doji(self, crow):
        return bool(constants.DOJI not in crow['tags'])
