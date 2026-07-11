"""
Backtesting engine.
"""

import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.data.market_data import MarketData
from src.backtesting.strategy import Strategy
from src.utils.logger import get_logger
from src.utils.exceptions import AnalysisError

logger = get_logger(__name__)


class Backtest:
    """
    Backtesting engine.
    """

    def __init__(self, market_data: MarketData, strategy: Strategy):
        """
        Initialize backtest.

        Args:
            market_data: MarketData instance
            strategy: Strategy instance
        """
        self.market_data = market_data
        self.strategy = strategy
        self.results: Dict[str, Any] = {}

    def run(
        self,
        symbol: str,
        timeframe: str = "1h",
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Run backtest.

        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe
            days: Number of days to backtest

        Returns:
            Backtest results
        """
        try:
            # Fetch historical data
            logger.info(f"Fetching {days} days of {timeframe} data for {symbol}...")
            limit = self._calculate_limit(days, timeframe)
            df = self.market_data.get_ohlcv(symbol, timeframe, limit=limit)

            if df is None or len(df) == 0:
                raise AnalysisError(f"No data available for {symbol}")

            # Generate signals
            logger.info(f"Generating signals with {self.strategy.name} strategy...")
            signals = self.strategy.generate_signals(df)

            # Calculate returns
            logger.info("Calculating returns...")
            performance = self.strategy.calculate_returns(df, signals)

            self.results = {
                "symbol": symbol,
                "strategy": self.strategy.name,
                "timeframe": timeframe,
                "start_date": df.index[0],
                "end_date": df.index[-1],
                "candles": len(df),
                "performance": performance,
            }

            return self.results
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            raise AnalysisError(f"Backtest error: {e}")

    @staticmethod
    def _calculate_limit(days: int, timeframe: str) -> int:
        """
        Calculate required candles for given days and timeframe.

        Args:
            days: Number of days
            timeframe: Candle timeframe

        Returns:
            Number of candles needed
        """
        timeframe_minutes = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "1h": 60,
            "4h": 240,
            "1d": 1440,
        }

        minutes_per_day = 24 * 60
        minutes_needed = days * minutes_per_day
        candle_minutes = timeframe_minutes.get(timeframe, 60)
        limit = int(minutes_needed / candle_minutes) + 100  # Extra buffer

        return min(limit, 1000)  # CCXT limit

    def print_results(self) -> None:
        """
        Print backtest results in human-readable format.
        """
        if not self.results:
            logger.warning("No backtest results to display")
            return

        perf = self.results.get("performance", {})

        print(f"""
╔════════════════════════════════════════════╗
║        BACKTEST RESULTS                   ║
╚════════════════════════════════════════════╝

Symbol: {self.results['symbol']}
Strategy: {self.results['strategy']}
Timeframe: {self.results['timeframe']}
Period: {self.results['start_date']} to {self.results['end_date']}
Candles: {self.results['candles']}

📊 Performance Metrics:
├─ Strategy Return: {perf.get('total_return', 0)}%
├─ Buy & Hold Return: {perf.get('buy_hold_return', 0)}%
├─ Sharpe Ratio: {perf.get('sharpe_ratio', 0)}
├─ Max Drawdown: {perf.get('max_drawdown', 0)}%
├─ Total Trades: {perf.get('num_trades', 0)}
└─ Win Rate: {perf.get('win_rate', 0)}%
        """)

    def compare_strategies(
        self,
        symbol: str,
        strategies: List[Strategy],
        timeframe: str = "1h",
        days: int = 30,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple strategies.

        Args:
            symbol: Trading symbol
            strategies: List of Strategy instances
            timeframe: Candle timeframe
            days: Number of days to backtest

        Returns:
            Comparison results
        """
        results = {}
        for strategy in strategies:
            backtest = Backtest(self.market_data, strategy)
            results[strategy.name] = backtest.run(symbol, timeframe, days)

        return results
