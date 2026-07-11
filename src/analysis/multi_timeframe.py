"""
Multi-timeframe analysis.
"""

import pandas as pd
from typing import Dict, Any
from src.data.market_data import MarketData
from src.indicators.moving_averages import MovingAverages
from src.indicators.momentum import Momentum
from src.indicators.volatility import Volatility
from src.utils.logger import get_logger
from src.utils.exceptions import AnalysisError

logger = get_logger(__name__)


class MultiTimeframeAnalysis:
    """
    Multi-timeframe technical analysis.
    """

    def __init__(self, market_data: MarketData):
        """
        Initialize multi-timeframe analysis.

        Args:
            market_data: MarketData instance
        """
        self.market_data = market_data

    def analyze(
        self,
        symbol: str,
        trend_tf: str = "15m",
        setup_tf: str = "5m",
        confirmation_tf: str = "1m",
    ) -> Dict[str, Any]:
        """
        Perform multi-timeframe analysis.

        Args:
            symbol: Trading symbol
            trend_tf: Trend timeframe
            setup_tf: Setup timeframe
            confirmation_tf: Confirmation timeframe

        Returns:
            Analysis results dictionary
        """
        try:
            # Get data for each timeframe
            trend_df = self.market_data.get_ohlcv(symbol, trend_tf)
            setup_df = self.market_data.get_ohlcv(symbol, setup_tf)
            confirmation_df = self.market_data.get_ohlcv(symbol, confirmation_tf)

            # Analyze each timeframe
            trend_analysis = self._analyze_timeframe(trend_df)
            setup_analysis = self._analyze_timeframe(setup_df)
            confirmation_analysis = self._analyze_timeframe(confirmation_df)

            return {
                "trend": trend_analysis,
                "setup": setup_analysis,
                "confirmation": confirmation_analysis,
            }
        except Exception as e:
            raise AnalysisError(f"Multi-timeframe analysis failed: {e}")

    @staticmethod
    def _analyze_timeframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze single timeframe.

        Args:
            df: OHLCV DataFrame

        Returns:
            Analysis results
        """
        # Calculate indicators
        emas = MovingAverages.calculate_ema_trend(df)
        rsi = Momentum.rsi(df)
        macd_line, signal_line, histogram = Momentum.macd(df)
        adx = Momentum.adx(df)
        atr = Volatility.atr(df)
        upper_bb, middle_bb, lower_bb = Volatility.bollinger_bands(df)

        # Get latest values
        latest = len(df) - 1
        current_price = df["close"].iloc[latest]
        current_rsi = rsi.iloc[latest]
        current_adx = adx.iloc[latest]
        current_atr = atr.iloc[latest]

        # Determine trend
        ema_20 = emas["ema_20"].iloc[latest]
        ema_50 = emas["ema_50"].iloc[latest]
        ema_200 = emas["ema_200"].iloc[latest]
        trend = MovingAverages.get_trend_direction(ema_20, ema_50, ema_200)

        # Check overbought/oversold
        rsi_signal = "overbought" if current_rsi > 70 else "oversold" if current_rsi < 30 else "neutral"

        return {
            "trend": trend,
            "current_price": current_price,
            "rsi": current_rsi,
            "adx": current_adx,
            "atr": current_atr,
            "rsi_signal": rsi_signal,
            "ema_20": ema_20,
            "ema_50": ema_50,
            "ema_200": ema_200,
            "macd": macd_line.iloc[latest],
            "signal_line": signal_line.iloc[latest],
            "histogram": histogram.iloc[latest],
            "bb_upper": upper_bb.iloc[latest],
            "bb_middle": middle_bb.iloc[latest],
            "bb_lower": lower_bb.iloc[latest],
        }
