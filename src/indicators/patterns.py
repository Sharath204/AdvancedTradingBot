"""
Candlestick pattern recognition.
"""

import pandas as pd
from typing import Dict, List
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CandlestickPatterns:
    """
    Candlestick pattern recognition.
    """

    @staticmethod
    def is_bullish_engulfing(df: pd.DataFrame) -> pd.Series:
        """
        Detect Bullish Engulfing pattern.
        """
        bullish = (
            (df["close"].shift(1) < df["open"].shift(1))
            & (df["close"] > df["open"])
            & (df["open"] <= df["close"].shift(1))
            & (df["close"] >= df["open"].shift(1))
        )
        return bullish

    @staticmethod
    def is_bearish_engulfing(df: pd.DataFrame) -> pd.Series:
        """
        Detect Bearish Engulfing pattern.
        """
        bearish = (
            (df["close"].shift(1) > df["open"].shift(1))
            & (df["close"] < df["open"])
            & (df["open"] >= df["close"].shift(1))
            & (df["close"] <= df["open"].shift(1))
        )
        return bearish

    @staticmethod
    def is_hammer(df: pd.DataFrame) -> pd.Series:
        """
        Detect Hammer pattern (bullish reversal).
        """
        body = abs(df["close"] - df["open"])
        lower_wick = df["open"].where(df["open"] < df["close"], df["close"]) - df["low"]
        upper_wick = df["high"] - df["close"].where(df["close"] > df["open"], df["open"])
        
        hammer = (lower_wick > 2 * body) & (upper_wick < 0.5 * body)
        return hammer

    @staticmethod
    def is_shooting_star(df: pd.DataFrame) -> pd.Series:
        """
        Detect Shooting Star pattern (bearish reversal).
        """
        body = abs(df["close"] - df["open"])
        upper_wick = df["high"] - df["close"].where(df["close"] > df["open"], df["open"])
        lower_wick = df["open"].where(df["open"] < df["close"], df["close"]) - df["low"]
        
        shooting_star = (upper_wick > 2 * body) & (lower_wick < 0.5 * body)
        return shooting_star

    @staticmethod
    def is_doji(df: pd.DataFrame, tolerance: float = 0.01) -> pd.Series:
        """
        Detect Doji pattern (indecision).
        """
        body = abs(df["close"] - df["open"])
        range_hl = df["high"] - df["low"]
        doji = body < (tolerance * range_hl)
        return doji

    @staticmethod
    def is_morning_star(df: pd.DataFrame) -> pd.Series:
        """
        Detect Morning Star pattern (bullish reversal).
        """
        # Three candle pattern
        pattern = (
            (df["close"].shift(2) < df["open"].shift(2))  # First candle bearish
            & (df["close"].shift(1) < df["open"].shift(1))  # Second candle small/bearish
            & (df["close"] > df["open"])  # Third candle bullish
            & (df["close"] > df["close"].shift(2))  # Closes above first candle
        )
        return pattern

    @staticmethod
    def is_evening_star(df: pd.DataFrame) -> pd.Series:
        """
        Detect Evening Star pattern (bearish reversal).
        """
        # Three candle pattern
        pattern = (
            (df["close"].shift(2) > df["open"].shift(2))  # First candle bullish
            & (df["close"].shift(1) > df["open"].shift(1))  # Second candle small/bullish
            & (df["close"] < df["open"])  # Third candle bearish
            & (df["close"] < df["close"].shift(2))  # Closes below first candle
        )
        return pattern

    @staticmethod
    def get_all_patterns(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Get all pattern signals for the latest candle.

        Args:
            df: OHLCV DataFrame

        Returns:
            Dictionary of pattern signals
        """
        if len(df) < 3:
            return {}

        latest = len(df) - 1
        patterns = {
            "bullish_engulfing": bool(CandlestickPatterns.is_bullish_engulfing(df).iloc[latest]),
            "bearish_engulfing": bool(CandlestickPatterns.is_bearish_engulfing(df).iloc[latest]),
            "hammer": bool(CandlestickPatterns.is_hammer(df).iloc[latest]),
            "shooting_star": bool(CandlestickPatterns.is_shooting_star(df).iloc[latest]),
            "doji": bool(CandlestickPatterns.is_doji(df).iloc[latest]),
            "morning_star": bool(CandlestickPatterns.is_morning_star(df).iloc[latest]),
            "evening_star": bool(CandlestickPatterns.is_evening_star(df).iloc[latest]),
        }
        return patterns
