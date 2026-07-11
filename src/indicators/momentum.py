"""
Momentum indicators.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Momentum:
    """
    Momentum indicators calculations.
    """

    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            data: Price series
            period: RSI period

        Returns:
            RSI values
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def macd(
        data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index.

        Args:
            df: OHLCV DataFrame
            period: ADX period

        Returns:
            ADX values
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        # Calculate Directional Movements
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        plus_dm[(plus_dm < minus_dm)] = 0
        minus_dm[(minus_dm < plus_dm)] = 0

        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        di_sum = plus_di + minus_di
        di_diff = abs(plus_di - minus_di)

        dx = 100 * (di_diff / di_sum)
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def roc(data: pd.Series, period: int = 12) -> pd.Series:
        """
        Calculate Rate of Change.

        Args:
            data: Price series
            period: ROC period

        Returns:
            ROC values
        """
        return ((data - data.shift(period)) / data.shift(period)) * 100

    @staticmethod
    def stochastic(
        df: pd.DataFrame, period: int = 14, smooth_k: int = 3, smooth_d: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator.

        Args:
            df: OHLCV DataFrame
            period: Lookback period
            smooth_k: K smoothing period
            smooth_d: D smoothing period

        Returns:
            Tuple of (%K, %D)
        """
        low_min = df["low"].rolling(window=period).min()
        high_max = df["high"].rolling(window=period).max()
        k_percent = 100 * ((df["close"] - low_min) / (high_max - low_min))
        k = k_percent.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()
        return k, d
