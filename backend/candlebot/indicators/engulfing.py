import talib
import pandas as pd


class IndicatorEngulfing:
    _id = 'engulfing'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        engulfing = talib.CDLENGULFING(
            df['open'], df['high'], df['low'], df['close'])
        engulfing = engulfing[engulfing != 0]
        df[cls._id] = engulfing
        return df
