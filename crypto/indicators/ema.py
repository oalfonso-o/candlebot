import pandas as pd

from crypto import settings


class IndicatorEMA:

    @staticmethod
    def apply(df: pd.DataFrame) -> pd.DataFrame:
        df['ema'] = df['close'].ewm(
            span=settings.BT_CONFIG['ema']['window'],
            adjust=settings.BT_CONFIG['ema']['adjust'],
        ).mean()
        return df
