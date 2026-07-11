"""
Telegram bot command handlers.
"""

from typing import Optional
from src.utils.logger import get_logger
from src.data.market_data import MarketData
from src.analysis.multi_timeframe import MultiTimeframeAnalysis
from src.analysis.signal_confidence import SignalConfidence

logger = get_logger(__name__)


class CommandHandlers:
    """
    Telegram command handlers.
    """

    def __init__(self, market_data: MarketData):
        """
        Initialize handlers.

        Args:
            market_data: MarketData instance
        """
        self.market_data = market_data
        self.mta = MultiTimeframeAnalysis(market_data)

    async def handle_analyze(self, symbol: str) -> str:
        """
        Handle /analyze command.

        Args:
            symbol: Trading symbol

        Returns:
            Analysis message
        """
        try:
            analysis = self.mta.analyze(symbol)
            confidence = SignalConfidence.calculate_confidence(analysis)

            message = self._format_analysis_message(symbol, analysis, confidence)
            return message
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return f"Error analyzing {symbol}: {str(e)}"

    async def handle_help(self) -> str:
        """
        Handle /help command.

        Returns:
            Help message
        """
        help_text = """
📊 **Telegram Market Analysis Bot Commands:**

/analyze <SYMBOL> - Analyze a trading pair (e.g., /analyze BTC/USDT)
/status - Get current bot status
/help - Show this help message
/settings - View/update bot settings

**Indicators Used:**
• EMA (20, 50, 200)
• RSI (14)
• MACD
• ADX
• ATR
• Bollinger Bands
• VWAP
• Support/Resistance
• Candlestick Patterns

**Multi-Timeframe Analysis:**
• 15m: Trend
• 5m: Setup
• 1m: Confirmation

**Signal Confidence Score:** 0-100 (higher = more confident)
        """
        return help_text

    async def handle_status(self) -> str:
        """
        Handle /status command.

        Returns:
            Status message
        """
        try:
            symbols = self.market_data.get_symbols()
            status_text = f"""
✅ **Bot Status: Online**

📈 Available Symbols: {len(symbols)}
🔄 Update Interval: 5 minutes
💾 Database: Active
📊 Analysis Module: Ready
            """
            return status_text
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return "❌ Error retrieving status"

    def _format_analysis_message(self, symbol: str, analysis: dict, confidence: dict) -> str:
        """
        Format analysis results as Telegram message.

        Args:
            symbol: Trading symbol
            analysis: Analysis results
            confidence: Confidence score

        Returns:
            Formatted message
        """
        trend_analysis = analysis.get("trend", {})
        setup_analysis = analysis.get("setup", {})
        confirmation_analysis = analysis.get("confirmation", {})
        overall_conf = confidence.get("overall_confidence", 0)

        # Determine signal emoji
        if overall_conf >= 70:
            signal_emoji = "🟢"
        elif overall_conf >= 50:
            signal_emoji = "🟡"
        else:
            signal_emoji = "🔴"

        message = f"""
{signal_emoji} **Analysis for {symbol}**

**📊 Confidence Score: {overall_conf}%**

**Trend Analysis (15m):**
• Trend: {trend_analysis.get('trend', 'N/A').upper()}
• RSI: {trend_analysis.get('rsi', 'N/A'):.2f}
• ADX: {trend_analysis.get('adx', 'N/A'):.2f}
• Price: ${trend_analysis.get('current_price', 'N/A'):.2f}

**Setup Analysis (5m):**
• Trend: {setup_analysis.get('trend', 'N/A').upper()}
• RSI: {setup_analysis.get('rsi', 'N/A'):.2f}
• MACD: {setup_analysis.get('macd', 'N/A'):.2f}

**Confirmation Analysis (1m):**
• Trend: {confirmation_analysis.get('trend', 'N/A').upper()}
• RSI: {confirmation_analysis.get('rsi', 'N/A'):.2f}
• ATR: {confirmation_analysis.get('atr', 'N/A'):.2f}

**Technical Levels:**
• EMA 20: ${trend_analysis.get('ema_20', 'N/A'):.2f}
• EMA 50: ${trend_analysis.get('ema_50', 'N/A'):.2f}
• EMA 200: ${trend_analysis.get('ema_200', 'N/A'):.2f}

⏰ Analysis generated at current market price
        """
        return message
