"""
Volatility indicators.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Volatility:
    """
    Volatility indicators calculations.
    """

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range.

        Args:
            df: OHLCV DataFrame
            period: ATR period

        Returns:
            ATR values
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    @staticmethod
    def bollinger_bands(
        data: pd.Series, period: int = 20, std_dev: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.

        Args:
            data: Price series
            period: Moving average period
            std_dev: Standard deviation multiplier

        Returns:
            Tuple of (Upper Band, Middle Band, Lower Band)
        """
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        return upper_band, middle_band, lower_band

    @staticmethod
    def keltner_channel(
        df: pd.DataFrame, period: int = 20, atr_mult: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Keltner Channel.

        Args:
            df: OHLCV DataFrame
            period: EMA period
            atr_mult: ATR multiplier

        Returns:
            Tuple of (Upper Channel, Middle Line, Lower Channel)
        """
        middle_line = df["close"].ewm(span=period).mean()
        atr = Volatility.atr(df, period)
        upper_channel = middle_line + (atr_mult * atr)
        lower_channel = middle_line - (atr_mult * atr)
        return upper_channel, middle_line, lower_channel

    @staticmethod
    def historical_volatility(
        data: pd.Series, period: int = 20
    ) -> pd.Series:
        """
        Calculate historical volatility (standard deviation).

        Args:
            data: Price series
            period: Lookback period

        Returns:
            Volatility values
        """
        returns = data.pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252)
        return volatility

    @staticmethod
    def donchian_channel(
        df: pd.DataFrame, period: int = 20
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Donchian Channel.

        Args:
            df: OHLCV DataFrame
            period: Lookback period

        Returns:
            Tuple of (Upper Channel, Lower Channel)
        """
        high_channel = df["high"].rolling(window=period).max()
        low_channel = df["low"].rolling(window=period).min()
        return high_channel, low_channel
