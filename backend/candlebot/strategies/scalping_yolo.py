from candlebot.indicators.ema import (
    IndicatorEMA10,
    IndicatorEMA20,
)
from candlebot.strategies.base import StrategyBase


class StrategyScalpingYolo(StrategyBase):
    _id = 'scalping_yolo'
    variables = []
    indicators = []
    len_queue = 15
    custom_df_ready_conditions = []
    direction_conditions = {
        'long': [],
        'short': [],
        'consolidation': [],
    }
    open_conditions = []
    post_open_actions = []
    close_win_conditions = [
        ('cond_close_win_pips_margin', 'close_win_pip_margin'),
    ]
    close_lose_conditions = [
        ('cond_close_lose_pips_margin', 'close_lose_pip_margin'),
    ]
    post_close_actions = []
    win_pips_margin = 30
    loss_pips_margin = 30
