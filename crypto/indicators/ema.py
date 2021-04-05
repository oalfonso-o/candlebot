import pandas as pd

from crypto import settings


class IndicatorEMA:

    _id = 'ema'

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df[cls._id] = df['close'].ewm(
            span=settings.BT['indicators'][cls._id]['span'],
            adjust=settings.BT['indicators'][cls._id]['adjust'],
        ).mean()
        return df
