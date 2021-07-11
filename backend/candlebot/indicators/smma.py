import pandas as pd


class IndicatorSMMA21:
    _id = 'smma21'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = smma(df, 21, cls._id)
        return df


class IndicatorSMMA50:
    _id = 'smma50'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = smma(df, 50, cls._id)
        return df


class IndicatorSMMA200:
    _id = 'smma200'
    variables = []

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = smma(df, 200, cls._id)
        return df


def smma(df, period, column_name, apply_to='close'):
    """Smoothed Moving Average (SMMA)

    https://github.com/dmitriiweb/tapy/blob/master/tapy/indicators.py
    ---------------------
        https://www.metatrader4.com/ru/trading-platform/help/analytics/tech_indicators/moving_average#smoothed_moving_average
        >>> Indicators.smma(period=5, column_name='smma', apply_to='Close')
        :param int period: the number of calculation periods, default: 5
        :param str column_name: Column name, default: smma
        :param str apply_to: Which column use for calculation.
            Can be *"Open"*, *"High"*, *"Low"* and *"Close"*.
            **Default**: Close
        :return: None
    """
    df_tmp = df[[apply_to]]
    first_val = df_tmp[apply_to].iloc[:period].mean()
    df_tmp = df_tmp.assign(column_name=None)
    df_tmp.at[period, column_name] = first_val
    for index, row in df_tmp.iterrows():
        if index > period:
            smma_val = (
                (
                    df_tmp.at[index - 1, column_name]
                    * (period - 1) + row[apply_to]
                ) / period
            )
            df_tmp.at[index, column_name] = smma_val
    df_tmp = df_tmp[[column_name]]
    df = df.merge(df_tmp, left_index=True, right_index=True)
    return df
