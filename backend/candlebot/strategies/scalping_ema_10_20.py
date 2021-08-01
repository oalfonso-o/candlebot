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
        # 'trend_long',
        'zigzag_trend_long',
        'circular_queue_is_full',
        # 'ago_2_open_gt_ema10',
        # 'ago_2_close_lt_ema10',
        # 'ago_2_color_red',
        # 'ago_1_high_lt_ema10',
        # 'crow_color_green',
        # 'crow_close_gt_ema10',
    ]
    post_open_actions = [
        'post_open_set_zigzag_stop_loss',
    ]
    close_win_conditions = [
        ('ema20_gt_ema10', 'close_win_generic'),
        ('crow_low_gt_open_pos', 'close_win_generic'),
    ]
    close_lose_conditions = [
        ('reached_stop_loss', 'close_by_stop_loss'),
    ]
