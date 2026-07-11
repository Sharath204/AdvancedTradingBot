"""
Strategy base class for backtesting.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Strategy(ABC):
    """
    Base class for trading strategies.
    """

    def __init__(self, name: str):
        """
        Initialize strategy.

        Args:
            name: Strategy name
        """
        self.name = name
        self.trades = []
        self.signals = []

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals.

        Args:
            df: OHLCV DataFrame

        Returns:
            Series with signals (1=buy, -1=sell, 0=hold)
        """
        pass

    def calculate_returns(self, df: pd.DataFrame, signals: pd.Series) -> Dict[str, float]:
        """
        Calculate strategy returns.

        Args:
            df: OHLCV DataFrame
            signals: Trading signals

        Returns:
            Performance metrics
        """
        df = df.copy()
        df["signals"] = signals
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signals"].shift(1) * df["returns"]

        cumulative_returns = (1 + df["strategy_returns"]).cumprod()
        total_return = (cumulative_returns.iloc[-1] - 1) * 100

        # Buy and hold comparison
        buy_hold_return = ((df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]) * 100

        # Sharpe ratio
        sharpe_ratio = (
            df["strategy_returns"].mean() / df["strategy_returns"].std() * (252**0.5)
            if df["strategy_returns"].std() != 0
            else 0
        )

        # Maximum drawdown
        cummax = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - cummax) / cummax
        max_drawdown = drawdown.min() * 100

        return {
            "total_return": round(total_return, 2),
            "buy_hold_return": round(buy_hold_return, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown, 2),
            "num_trades": int((signals != 0).sum()),
            "win_rate": self._calculate_win_rate(df),
        }

    def _calculate_win_rate(self, df: pd.DataFrame) -> float:
        """
        Calculate win rate from trades.

        Args:
            df: DataFrame with strategy_returns column

        Returns:
            Win rate percentage
        """
        winning_trades = (df["strategy_returns"] > 0).sum()
        total_trades = (df["strategy_returns"] != 0).sum()
        return round((winning_trades / total_trades * 100) if total_trades > 0 else 0, 2)


class EMACrossoverStrategy(Strategy):
    """
    EMA Crossover Strategy.
    """

    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        """
        Initialize EMA Crossover Strategy.

        Args:
            fast_period: Fast EMA period
            slow_period: Slow EMA period
        """
        super().__init__("EMA Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate EMA crossover signals.

        Args:
            df: OHLCV DataFrame

        Returns:
            Trading signals
        """
        df = df.copy()
        df["ema_fast"] = df["close"].ewm(span=self.fast_period).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow_period).mean()

        df["signal"] = 0
        df.loc[df["ema_fast"] > df["ema_slow"], "signal"] = 1
        df.loc[df["ema_fast"] < df["ema_slow"], "signal"] = -1

        return df["signal"]


class RSIStrategy(Strategy):
    """
    RSI Mean Reversion Strategy.
    """

    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        """
        Initialize RSI Strategy.

        Args:
            period: RSI period
            oversold: Oversold level
            overbought: Overbought level
        """
        super().__init__("RSI Mean Reversion")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate RSI signals.

        Args:
            df: OHLCV DataFrame

        Returns:
            Trading signals
        """
        df = df.copy()
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        df["signal"] = 0
        df.loc[rsi < self.oversold, "signal"] = 1  # Buy
        df.loc[rsi > self.overbought, "signal"] = -1  # Sell

        return df["signal"]
