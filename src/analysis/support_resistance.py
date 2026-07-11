"""
Support and Resistance detection.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SupportResistance:
    """
    Support and Resistance level detection.
    """

    @staticmethod
    def find_support_resistance(
        df: pd.DataFrame, lookback: int = 30, threshold: float = 0.02
    ) -> Tuple[List[float], List[float]]:
        """
        Find support and resistance levels.

        Args:
            df: OHLCV DataFrame
            lookback: Number of periods to analyze
            threshold: Price proximity threshold for grouping levels

        Returns:
            Tuple of (support levels, resistance levels)
        """
        high = df["high"].iloc[-lookback:]
        low = df["low"].iloc[-lookback:]
        close = df["close"].iloc[-lookback:]

        # Find local extremes
        support_levels = []
        resistance_levels = []

        for i in range(1, len(low) - 1):
            # Support: local minimum
            if low.iloc[i] < low.iloc[i - 1] and low.iloc[i] < low.iloc[i + 1]:
                support_levels.append(low.iloc[i])

            # Resistance: local maximum
            if high.iloc[i] > high.iloc[i - 1] and high.iloc[i] > high.iloc[i + 1]:
                resistance_levels.append(high.iloc[i])

        # Group similar levels
        support_levels = SupportResistance._group_levels(
            support_levels, close.iloc[-1], threshold
        )
        resistance_levels = SupportResistance._group_levels(
            resistance_levels, close.iloc[-1], threshold
        )

        return sorted(support_levels), sorted(resistance_levels, reverse=True)

    @staticmethod
    def _group_levels(
        levels: List[float], current_price: float, threshold: float
    ) -> List[float]:
        """
        Group similar price levels.

        Args:
            levels: List of price levels
            current_price: Current price
            threshold: Threshold for grouping

        Returns:
            Grouped levels
        """
        if not levels:
            return []

        levels = sorted(levels)
        grouped = []
        current_group = [levels[0]]

        for level in levels[1:]:
            if abs(level - current_group[-1]) / current_group[-1] <= threshold:
                current_group.append(level)
            else:
                grouped.append(np.mean(current_group))
                current_group = [level]

        grouped.append(np.mean(current_group))
        return grouped

    @staticmethod
    def get_nearest_support(current_price: float, supports: List[float]) -> float:
        """
        Get nearest support level below current price.

        Args:
            current_price: Current price
            supports: List of support levels

        Returns:
            Nearest support level
        """
        below = [s for s in supports if s < current_price]
        return max(below) if below else min(supports) if supports else 0

    @staticmethod
    def get_nearest_resistance(current_price: float, resistances: List[float]) -> float:
        """
        Get nearest resistance level above current price.

        Args:
            current_price: Current price
            resistances: List of resistance levels

        Returns:
            Nearest resistance level
        """
        above = [r for r in resistances if r > current_price]
        return min(above) if above else max(resistances) if resistances else 0

    @staticmethod
    def calculate_pivot_points(
        df: pd.DataFrame,
    ) -> Dict[str, float]:
        """
        Calculate Pivot Points for support/resistance.

        Args:
            df: OHLCV DataFrame

        Returns:
            Dictionary with pivot points
        """
        high = df["high"].iloc[-1]
        low = df["low"].iloc[-1]
        close = df["close"].iloc[-1]

        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)

        return {
            "pivot": pivot,
            "r1": r1,
            "r2": r2,
            "s1": s1,
            "s2": s2,
        }
