import pandas as pd
# from ta import add_all_ta_features
# from ta.utils import dropna

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
        # df = dropna(df)
        # df = add_all_ta_features(
        #     df, open="open", high="high", low="low", close="close",
        #     volume="volume", fillna=True
        # )
        return df
