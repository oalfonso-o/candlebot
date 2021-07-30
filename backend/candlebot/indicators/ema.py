import pandas as pd

from candlebot.settings import Settings


class IndicatorEMA:
    _id = 'ema'
    variables = [
        {'name': 'span', 'type': 'num'},
        {'name': 'adjust', 'type': 'bool'},
    ]

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df[cls._id] = df['close'].ewm(
            span=Settings.BT['indicators'][cls._id]['span'],
            adjust=Settings.BT['indicators'][cls._id]['adjust'],
        ).mean()
        return df


class IndicatorEMA10:
    _id = 'ema10'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df[cls._id] = df['close'].ewm(span=10, adjust=False).mean()
        return df


class IndicatorEMA20:
    _id = 'ema20'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df[cls._id] = df['close'].ewm(span=20, adjust=False).mean()
        return df
