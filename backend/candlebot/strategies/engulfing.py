import logging
from typing import Tuple

import pandas as pd

from candlebot import utils
from candlebot.indicators.engulfing import IndicatorEngulfing
from candlebot.models.wallet import Wallet

logger = logging.getLogger(__name__)


class StrategyEngulfing:
    _id = 'engulfing'
    indicators = [IndicatorEngulfing]
    variables = []

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.wallet = Wallet()
        for indicator in self.indicators:
            self.df = indicator.apply(self.df)

    def calc(self) -> Tuple[pd.DataFrame, dict]:
        for i, row in self.df.iterrows():
            if self._must_open_long(row):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.open_pos('long', row['close'], timestamp)
            elif self._must_close_long(row):
                timestamp = utils.datetime_to_timestamp(
                    row['_id'].to_pydatetime()
                )
                self.wallet.close_pos('long', row['close'], timestamp)
        return self.df, self.wallet

    def _must_open_long(self, row):
        return False

    def _must_close_long(self, row):
        return False
