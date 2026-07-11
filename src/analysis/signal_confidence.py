"""
Signal confidence scoring.
"""

from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SignalConfidence:
    """
    Calculate confidence score for trading signals.
    """

    # Default weights for different factors
    DEFAULT_WEIGHTS = {
        "ema_trend": 0.20,
        "rsi_divergence": 0.15,
        "macd_crossover": 0.15,
        "adx_strength": 0.15,
        "bollinger_bands": 0.15,
        "volume_profile": 0.10,
        "pattern_recognition": 0.10,
    }

    @staticmethod
    def calculate_confidence(
        analysis: Dict[str, Any], weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall confidence score for a signal.

        Args:
            analysis: Multi-timeframe analysis results
            weights: Custom weights for indicators

        Returns:
            Confidence score and breakdown
        """
        if weights is None:
            weights = SignalConfidence.DEFAULT_WEIGHTS

        scores = {}

        # EMA Trend score (0-100)
        trend_score = SignalConfidence._score_trend(analysis)
        scores["ema_trend"] = trend_score

        # RSI signal (0-100)
        rsi_score = SignalConfidence._score_rsi(analysis)
        scores["rsi_divergence"] = rsi_score

        # MACD signal (0-100)
        macd_score = SignalConfidence._score_macd(analysis)
        scores["macd_crossover"] = macd_score

        # ADX strength (0-100)
        adx_score = SignalConfidence._score_adx(analysis)
        scores["adx_strength"] = adx_score

        # Bollinger Bands (0-100)
        bb_score = SignalConfidence._score_bollinger_bands(analysis)
        scores["bollinger_bands"] = bb_score

        # Volume profile (0-100) - placeholder
        volume_score = 50
        scores["volume_profile"] = volume_score

        # Pattern recognition (0-100) - placeholder
        pattern_score = 50
        scores["pattern_recognition"] = pattern_score

        # Calculate weighted confidence
        total_confidence = sum(
            scores.get(key, 0) * weights.get(key, 0) for key in weights
        )

        return {
            "overall_confidence": round(total_confidence, 2),
            "breakdown": scores,
            "weights": weights,
        }

    @staticmethod
    def _score_trend(analysis: Dict[str, Any]) -> float:
        """
        Score trend alignment across timeframes.
        """
        score = 50  # neutral
        trends = [
            analysis.get("trend", {}).get("trend"),
            analysis.get("setup", {}).get("trend"),
            analysis.get("confirmation", {}).get("trend"),
        ]

        bullish_count = sum(1 for t in trends if t == "bullish")
        bearish_count = sum(1 for t in trends if t == "bearish")

        if bullish_count == 3:
            score = 100
        elif bullish_count == 2:
            score = 75
        elif bearish_count == 3:
            score = 0
        elif bearish_count == 2:
            score = 25

        return score

    @staticmethod
    def _score_rsi(analysis: Dict[str, Any]) -> float:
        """
        Score RSI signals.
        """
        score = 50  # neutral
        rsi_values = [
            analysis.get(key, {}).get("rsi") for key in ["trend", "setup", "confirmation"]
        ]

        # Average RSI
        avg_rsi = sum(r for r in rsi_values if r is not None) / len(
            [r for r in rsi_values if r is not None]
        )

        if avg_rsi > 70:
            score = 25  # overbought
        elif avg_rsi < 30:
            score = 75  # oversold (bullish)
        elif 40 < avg_rsi < 60:
            score = 50  # neutral

        return score

    @staticmethod
    def _score_macd(analysis: Dict[str, Any]) -> float:
        """
        Score MACD signals.
        """
        score = 50  # neutral
        histograms = [
            analysis.get(key, {}).get("histogram") for key in ["trend", "setup", "confirmation"]
        ]

        positive_count = sum(1 for h in histograms if h is not None and h > 0)
        negative_count = sum(1 for h in histograms if h is not None and h < 0)

        if positive_count == 3:
            score = 100
        elif positive_count == 2:
            score = 75
        elif negative_count == 3:
            score = 0
        elif negative_count == 2:
            score = 25

        return score

    @staticmethod
    def _score_adx(analysis: Dict[str, Any]) -> float:
        """
        Score ADX trend strength.
        """
        adx_values = [
            analysis.get(key, {}).get("adx") for key in ["trend", "setup", "confirmation"]
        ]
        avg_adx = sum(a for a in adx_values if a is not None) / len(
            [a for a in adx_values if a is not None]
        )

        if avg_adx > 40:
            return 100  # strong trend
        elif avg_adx > 25:
            return 75  # moderate trend
        elif avg_adx > 15:
            return 50  # weak trend
        else:
            return 25  # no trend

    @staticmethod
    def _score_bollinger_bands(analysis: Dict[str, Any]) -> float:
        """
        Score Bollinger Bands positioning.
        """
        score = 50  # neutral
        for tf in ["trend", "setup", "confirmation"]:
            tf_data = analysis.get(tf, {})
            price = tf_data.get("current_price")
            bb_upper = tf_data.get("bb_upper")
            bb_lower = tf_data.get("bb_lower")
            bb_middle = tf_data.get("bb_middle")

            if price and bb_upper and bb_lower and bb_middle:
                if price > bb_upper:
                    score = max(score - 10, 0)  # overbought
                elif price < bb_lower:
                    score = min(score + 10, 100)  # oversold

        return score
