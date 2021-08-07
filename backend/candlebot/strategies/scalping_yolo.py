from candlebot.strategies.base import StrategyBase
from candlebot.indicators.ema import (
    IndicatorEMA10,
    IndicatorEMA20,
)
from candlebot.indicators.william_fractal import IndicatorWilliamBullFractals


class StrategyScalpingYolo(StrategyBase):
    _id = 'scalping_yolo'
    variables = []
    indicators = [
        IndicatorEMA10,
        IndicatorEMA20,
    ]
    markers_indicators = [
        IndicatorWilliamBullFractals,
    ]
    len_queue = 15
    custom_df_ready_conditions = []
    direction_conditions = {
        'long': ['ema10_gt_ema20'],
        'short': ['ema20_gt_ema10'],
        'consolidation': [],
    }
    open_conditions = [
        'trend_long',
        'all_5_prev_rows_ema10_gt_ema20',
        'crow_color_green',
        'crow_close_gt_ema10',
    ]
    post_open_actions = []
    close_win_conditions = [
        ('cond_close_win_pips_margin', 'close_win_pip_margin'),
    ]
    close_lose_conditions = [
        ('cond_close_lose_pips_margin', 'close_lose_pip_margin'),
    ]
    win_pips_margin = 30
    loss_pips_margin = 30
