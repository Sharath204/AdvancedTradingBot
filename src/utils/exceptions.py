"""
Custom exceptions for the Telegram Market Analysis Bot.
"""


class BotException(Exception):
    """Base exception for the bot."""
    pass


class ConfigError(BotException):
    """Raised when configuration is invalid."""
    pass


class MarketDataError(BotException):
    """Raised when market data fetch fails."""
    pass


class IndicatorError(BotException):
    """Raised when indicator calculation fails."""
    pass


class AnalysisError(BotException):
    """Raised when analysis fails."""
    pass


class DatabaseError(BotException):
    """Raised when database operation fails."""
    pass


class TelegramError(BotException):
    """Raised when Telegram operation fails."""
    pass


class SignalGenerationError(BotException):
    """Raised when signal generation fails."""
    pass
