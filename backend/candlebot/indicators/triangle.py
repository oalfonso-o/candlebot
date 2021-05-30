from abc import ABCMeta

import pandas as pd


class IndicatorMABase(metaclass=ABCMeta):
    _id = 'ma'
    variables = []
    value = 0

    @classmethod
    def apply(cls, df: pd.DataFrame) -> pd.DataFrame:
        df[cls._id] = df['close'].rolling(window=cls.value).mean()
        return df


class IndicatorMA200(IndicatorMABase):
    _id = 'ma200'
    value = 200


class IndicatorMA50(IndicatorMABase):
    _id = 'ma50'
    value = 50


class IndicatorMA20(IndicatorMABase):
    _id = 'ma20'
    value = 20
