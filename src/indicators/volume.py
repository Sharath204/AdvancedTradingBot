"""
Volume indicators.
"""

import pandas as pd
from typing import Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Volume:
    """
    Volume indicators calculations.
    """

    @staticmethod
    def vwap(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price.

        Args:
            df: OHLCV DataFrame

        Returns:
            VWAP values
        """
        typical_price = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (
            (typical_price * df["volume"]).rolling(window=len(df)).sum()
            / df["volume"].rolling(window=len(df)).sum()
        )
        return vwap

    @staticmethod
    def on_balance_volume(df: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume.

        Args:
            df: OHLCV DataFrame

        Returns:
            OBV values
        """
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = df["volume"].iloc[0]

        for i in range(1, len(df)):
            if df["close"].iloc[i] > df["close"].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + df["volume"].iloc[i]
            elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - df["volume"].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    @staticmethod
    def money_flow_index(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Money Flow Index.

        Args:
            df: OHLCV DataFrame
            period: MFI period

        Returns:
            MFI values
        """
        typical_price = (df["high"] + df["low"] + df["close"]) / 3
        money_flow = typical_price * df["volume"]

        positive_flow = pd.Series(0.0, index=df.index)
        negative_flow = pd.Series(0.0, index=df.index)

        for i in range(1, len(df)):
            if typical_price.iloc[i] > typical_price.iloc[i - 1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
            else:
                negative_flow.iloc[i] = money_flow.iloc[i]

        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()

        money_flow_ratio = positive_mf / negative_mf
        mfi = 100 - (100 / (1 + money_flow_ratio))

        return mfi

    @staticmethod
    def accumulation_distribution(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Accumulation/Distribution Line.

        Args:
            df: OHLCV DataFrame

        Returns:
            A/D values
        """
        clv = (
            (df["close"] - df["low"]) - (df["high"] - df["close"])
        ) / (df["high"] - df["low"])
        ad = (clv * df["volume"]).cumsum()
        return ad

    @staticmethod
    def volume_rate_of_change(
        df: pd.DataFrame, period: int = 12
    ) -> pd.Series:
        """
        Calculate Volume Rate of Change.

        Args:
            df: OHLCV DataFrame
            period: VROC period

        Returns:
            VROC values
        """
        vroc = (
            (df["volume"] - df["volume"].shift(period))
            / df["volume"].shift(period)
        ) * 100
        return vroc
