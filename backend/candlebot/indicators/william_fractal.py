import pandas as pd
import numpy as np


class IndicatorWilliamBullFractals:
    _id = 'william_bull_fractals'
    text = 'bull fractal'
    position = 'belowBar'
    color = 'green'
    shape = 'arrowUp'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        """William Bull Fractals

        https://github.com/dmitriiweb/tapy/blob/master/tapy/indicators.py
        ---------
            https://www.metatrader4.com/en/trading-platform/help/analytics/tech_indicators/fractals
        """
        df_tmp = df[['low']]
        df_tmp = df_tmp.assign(
            william_bull_fractals=np.where(
                (
                    (df_tmp['low'] < df_tmp['low'].shift(1))
                    & (df_tmp['low'] < df_tmp['low'].shift(2))
                    & (df_tmp['low'] < df_tmp['low'].shift(-1))
                    & (df_tmp['low'] < df_tmp['low'].shift(-2))
                ),
                True,
                False,
            )
        )

        df[cls._id] = df_tmp['william_bull_fractals']

        return df


class IndicatorWilliamBearFractals:
    _id = 'william_bear_fractals'
    text = 'bear fractal'
    position = 'aboveBar'
    color = 'red'
    shape = 'arrowDown'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        """William Bear Fractals

        https://github.com/dmitriiweb/tapy/blob/master/tapy/indicators.py
        ---------
            https://www.metatrader4.com/en/trading-platform/help/analytics/tech_indicators/fractals
        """
        df_tmp = df[['high']]
        df_tmp = df_tmp.assign(
            william_bear_fractals=np.where(
                (
                    (df_tmp['high'] > df_tmp['high'].shift(1))
                    & (df_tmp['high'] > df_tmp['high'].shift(2))
                    & (df_tmp['high'] > df_tmp['high'].shift(-1))
                    & (df_tmp['high'] > df_tmp['high'].shift(-2))
                ),
                True,
                False,
            )
        )

        df[cls._id] = df_tmp['william_bear_fractals']

        return df
