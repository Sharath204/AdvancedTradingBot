"""
Moving averages indicators.
"""

import pandas as pd
from typing import Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MovingAverages:
    """
    Moving averages calculations.
    """

    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.

        Args:
            data: Price series
            period: EMA period

        Returns:
            EMA values
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average.

        Args:
            data: Price series
            period: SMA period

        Returns:
            SMA values
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def wma(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Weighted Moving Average.

        Args:
            data: Price series
            period: WMA period

        Returns:
            WMA values
        """
        weights = pd.Series(range(1, period + 1))
        return data.rolling(window=period).apply(
            lambda x: (weights * x).sum() / weights.sum(), raw=False
        )

    @staticmethod
    def calculate_ema_trend(
        df: pd.DataFrame, periods: list = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate EMAs and determine trend.

        Args:
            df: OHLCV DataFrame
            periods: List of EMA periods

        Returns:
            Dictionary of EMA values
        """
        if periods is None:
            periods = [20, 50, 200]

        emas = {}
        for period in periods:
            emas[f"ema_{period}"] = MovingAverages.ema(df["close"], period)

        return emas

    @staticmethod
    def get_trend_direction(ema_20: float, ema_50: float, ema_200: float) -> str:
        """
        Determine trend direction from EMAs.

        Args:
            ema_20: Current EMA 20 value
            ema_50: Current EMA 50 value
            ema_200: Current EMA 200 value

        Returns:
            Trend direction: 'bullish', 'bearish', or 'neutral'
        """
        if ema_20 > ema_50 > ema_200:
            return "bullish"
        elif ema_20 < ema_50 < ema_200:
            return "bearish"
        else:
            return "neutral"
