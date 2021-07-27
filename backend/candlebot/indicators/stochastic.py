import ta
import pandas as pd

from candlebot.settings import Settings


class IndicatorStochRSI:
    variables = [
        # {'name': 'window', 'type': 'num'},
        # {'name': 'smooth1', 'type': 'num'},
        # {'name': 'smooth2', 'type': 'num'},
        # {'name': 'fillna', 'type': 'bool'},
    ]

    @staticmethod
    def _get_stoch_rsi(df):
        window = Settings.BT['indicators']['stoch_rsi']['window']
        if type(window) == list:
            window = window[0]
        smooth1 = Settings.BT['indicators']['stoch_rsi']['smooth1']
        if type(smooth1) == list:
            smooth1 = smooth1[0]
        smooth2 = Settings.BT['indicators']['stoch_rsi']['smooth2']
        if type(smooth2) == list:
            smooth2 = smooth2[0]
        fillna = Settings.BT['indicators']['stoch_rsi']['fillna']
        if type(fillna) == list:
            fillna = fillna[0]
        return ta.momentum.StochRSIIndicator(
            df['close'],
            window=window,
            smooth1=smooth1,
            smooth2=smooth2,
            fillna=fillna,
        )


class IndicatorStochRSIK(IndicatorStochRSI):
    _id = 'stoch_rsi_k'

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        objects = cls._get_stoch_rsi(df)
        df[cls._id] = objects.stochrsi_k()
        return df


class IndicatorStochRSID(IndicatorStochRSI):
    _id = 'stoch_rsi_d'

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        objects = cls._get_stoch_rsi(df)
        df[cls._id] = objects.stochrsi_d()
        return df
