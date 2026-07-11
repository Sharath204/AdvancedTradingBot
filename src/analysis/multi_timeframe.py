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
        self.market_data = market_data

    def analyze(
        self,
        symbol: str,
        trend_tf: str = "15m",
        setup_tf: str = "5m",
        confirmation_tf: str = "1m",
    ) -> Dict[str, Any]:

        try:

            trend_df = self.market_data.get_ohlcv(symbol, trend_tf)
            setup_df = self.market_data.get_ohlcv(symbol, setup_tf)
            confirmation_df = self.market_data.get_ohlcv(symbol, confirmation_tf)

            trend_analysis = self._analyze_timeframe(trend_df)
            setup_analysis = self._analyze_timeframe(setup_df)
            confirmation_analysis = self._analyze_timeframe(confirmation_df)

            return {
                "trend": trend_analysis,
                "setup": setup_analysis,
                "confirmation": confirmation_analysis,
            }

        except Exception as e:
            raise AnalysisError(
                f"Multi-timeframe analysis failed: {e}"
            )

    @staticmethod
    def _analyze_timeframe(df: pd.DataFrame) -> Dict[str, Any]:

        # Calculate indicators
        emas = MovingAverages.calculate_ema_trend(df)

        # Indicators using close price
        rsi = Momentum.rsi(df["close"])
        macd_line, signal_line, histogram = Momentum.macd(df["close"])
        upper_bb, middle_bb, lower_bb = Volatility.bollinger_bands(df["close"])

        # Indicators using OHLC
        adx = Momentum.adx(df)
        atr = Volatility.atr(df)

        latest = len(df) - 1

        current_price = float(df["close"].iloc[latest])
        current_rsi = float(rsi.iloc[latest])
        current_adx = float(adx.iloc[latest])
        current_atr = float(atr.iloc[latest])

        ema_20 = float(emas["ema_20"].iloc[latest])
        ema_50 = float(emas["ema_50"].iloc[latest])
        ema_200 = float(emas["ema_200"].iloc[latest])

        trend = MovingAverages.get_trend_direction(
            ema_20,
            ema_50,
            ema_200
        )

        if current_rsi > 70:
            rsi_signal = "overbought"
        elif current_rsi < 30:
            rsi_signal = "oversold"
        else:
            rsi_signal = "neutral"

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
            "macd": float(macd_line.iloc[latest]),
            "signal_line": float(signal_line.iloc[latest]),
            "histogram": float(histogram.iloc[latest]),
            "bb_upper": float(upper_bb.iloc[latest]),
            "bb_middle": float(middle_bb.iloc[latest]),
            "bb_lower": float(lower_bb.iloc[latest]),
        }