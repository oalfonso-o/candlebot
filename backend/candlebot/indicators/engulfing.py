import talib
import pandas as pd


class IndicatorEngulfingBull:
    _id = 'engulfing_bull'
    text = 'bull engulfing'
    position = 'belowBar'
    color = 'green'
    shape = 'arrowUp'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        engulfing = talib.CDLENGULFING(
            df['open'], df['high'], df['low'], df['close'])
        engulfing = engulfing.replace({0: False, -100: False, 100: True})
        df[cls._id] = engulfing
        return df


class IndicatorEngulfingBear:
    _id = 'engulfing_bear'
    text = 'bear engulfing'
    position = 'aboveBar'
    color = 'red'
    shape = 'arrowDown'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        engulfing = talib.CDLENGULFING(
            df['open'], df['high'], df['low'], df['close'])
        engulfing = engulfing.replace({0: False, -100: True, 100: False})
        df[cls._id] = engulfing
        return df
