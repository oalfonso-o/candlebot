from candlebot.indicators.ema import (
    IndicatorEMA10,
    IndicatorEMA20,
)
from candlebot.indicators.zigzag import IndicatorZigZag
from candlebot.strategies.base import StrategyBase


class StrategyScalpingEMA10_20(StrategyBase):
    _id = 'scalping_ema_10_20'
    variables = []
    indicators = [
        IndicatorEMA10,
        IndicatorEMA20,
        IndicatorZigZag,
    ]
    len_queue = 200
    custom_df_ready_conditions = [
        'ema10_is_not_nan',
        'ema20_is_not_nan',
    ]
    direction_conditions = {
        'long': ['ema10_gt_ema20'],
        'short': ['ema20_gt_ema10'],
        'consolidation': [],
    }
    open_conditions = [
        'zigzag_trend_long',
        'trend_long',
        'all_5_prev_rows_ema10_gt_ema20',
        'crow_color_green',
        'crow_close_gt_ema10',
        [
            [
                'ago_2_open_gt_ema10',
                'ago_2_close_lt_ema10',
                'ago_2_color_red',
                'ago_1_high_lt_ema10',
            ],
            [
                'ago_3_open_gt_ema10',
                'ago_3_close_lt_ema10',
                'ago_3_color_red',
                'ago_2_close_lt_ema10',
                'ago_2_close_lt_ema10',
            ],
        ],
    ]
    post_open_actions = [
        'post_open_set_zigzag_stop_loss',
    ]
    close_win_conditions = [  # these are OR conditions
        ('cond_close_win_pips_margin', 'close_win_pip_margin'),
        # ('ema20_gt_ema10', 'close_win_generic'),
        # ('crow_low_gt_open_pos', 'close_win_generic'),
    ]
    close_lose_conditions = [  # these are OR conditions
        ('cond_close_lose_pips_margin', 'close_lose_pip_margin'),
        # ('reached_stop_loss', 'close_by_stop_loss'),
    ]
    # post_close_actions = []  # if uncommented this overrides the base
    win_pips_margin = 20
    loss_pips_margin = 40
