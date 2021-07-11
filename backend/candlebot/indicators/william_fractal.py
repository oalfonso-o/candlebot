import pandas as pd
import numpy as np

WILLIAM_FRACTALS_PERIODS = (-2, -1, 1, 2)


class IndicatorWilliamBullFractals:
    _id = 'william_bull_fractals'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        bull_fractals = pd.Series(
            np.logical_and.reduce([
                df['low'] < df['low'].shift(period)
                for period in WILLIAM_FRACTALS_PERIODS
            ]),
            index=df.index,
        )

        df[cls._id] = bull_fractals

        return df


class IndicatorWilliamBearFractals:
    _id = 'william_bear_fractals'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        bull_fractals = pd.Series(
            np.logical_and.reduce([
                df['high'] > df['high'].shift(period)
                for period in WILLIAM_FRACTALS_PERIODS
            ]),
            index=df.index,
        )

        df[cls._id] = bull_fractals

        return df
