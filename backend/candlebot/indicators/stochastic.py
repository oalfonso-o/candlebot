import ta
import pandas as pd

from candlebot.settings import Settings


class IndicatorStochRSIK:
    _id = 'stoch_rsi_k'
    variables = [
        {'name': 'window', 'type': 'num'},
        {'name': 'smooth1', 'type': 'num'},
        {'name': 'smooth2', 'type': 'num'},
        {'name': 'fillna', 'type': 'bool'},
    ]

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        objects = ta.momentum.StochRSIIndicator(
            df['close'],
            window=Settings.BT['indicators']['stoch_rsi']['window'],
            smooth1=Settings.BT['indicators']['stoch_rsi']['smooth1'],
            smooth2=Settings.BT['indicators']['stoch_rsi']['smooth2'],
            fillna=Settings.BT['indicators']['stoch_rsi']['fillna'],
        )
        df[cls._id] = objects.stochrsi_k()
        return df


class IndicatorStochRSID:
    _id = 'stoch_rsi_d'
    variables = [
        {'name': 'window', 'type': 'num'},
        {'name': 'smooth1', 'type': 'num'},
        {'name': 'smooth2', 'type': 'num'},
        {'name': 'fillna', 'type': 'bool'},
    ]

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        objects = ta.momentum.StochRSIIndicator(
            df['close'],
            window=Settings.BT['indicators']['stoch_rsi']['window'],
            smooth1=Settings.BT['indicators']['stoch_rsi']['smooth1'],
            smooth2=Settings.BT['indicators']['stoch_rsi']['smooth2'],
            fillna=Settings.BT['indicators']['stoch_rsi']['fillna'],
        )
        df[cls._id] = objects.stochrsi_d()
        return df
