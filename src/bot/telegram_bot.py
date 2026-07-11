"""
Telegram bot main class.
"""

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from src.utils.logger import get_logger
from src.utils.config import Config
from src.data.market_data import MarketData
from src.bot.handlers import CommandHandlers
from src.utils.exceptions import TelegramError
import logging

logger = get_logger(__name__)


class TelegramBot:
    """
    Telegram bot main class.
    """

    def __init__(self, config: Config):
        """
        Initialize Telegram bot.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.telegram_config = config.get_telegram_config()
        self.market_data = MarketData(
            exchange_name="binance",
            config=config.get_binance_config(),
        )
        self.handlers = CommandHandlers(self.market_data)
        self.application: Application = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command.

        Args:
            update: Telegram update
            context: Telegram context
        """
        welcome_message = """
        🤖 **Welcome to Market Analysis Bot!**

        I can analyze cryptocurrency markets in real-time using advanced technical indicators.

        Use /help to see available commands.
        Use /analyze <SYMBOL> to analyze a trading pair.

        Example: /analyze BTC/USDT
        """
        await update.message.reply_text(welcome_message, parse_mode="Markdown")
        logger.info(f"User {update.effective_user.id} started the bot")

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /analyze command.

        Args:
            update: Telegram update
            context: Telegram context
        """
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a symbol. Example: /analyze BTC/USDT"
            )
            return

        symbol = context.args[0].upper()

        # Validate symbol format
        if "/" not in symbol:
            symbol = f"{symbol}/USDT"

        try:
            await update.message.reply_text(f"📊 Analyzing {symbol}...")
            analysis_message = await self.handlers.handle_analyze(symbol)
            await update.message.reply_text(analysis_message, parse_mode="Markdown")
            logger.info(f"Analysis completed for {symbol}")
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            await update.message.reply_text(
                f"❌ Error analyzing {symbol}: {str(e)}"
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command.

        Args:
            update: Telegram update
            context: Telegram context
        """
        help_message = await self.handlers.handle_help()
        await update.message.reply_text(help_message, parse_mode="Markdown")
        logger.info("Help command requested")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /status command.

        Args:
            update: Telegram update
            context: Telegram context
        """
        status_message = await self.handlers.handle_status()
        await update.message.reply_text(status_message, parse_mode="Markdown")
        logger.info("Status command requested")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle errors.

        Args:
            update: Telegram update
            context: Telegram context
        """
        logger.error(f"Exception while handling an update: {context.error}")
        if update and update.message:
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )

    async def initialize(self) -> None:
        """
        Initialize the bot application.

        Raises:
            TelegramError: If bot initialization fails
        """
        try:
            bot_token = self.telegram_config.get("bot_token")
            if not bot_token:
                raise TelegramError("Bot token not configured")

            self.application = Application.builder().token(bot_token).build()

            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("analyze", self.analyze))
            self.application.add_handler(CommandHandler("help", self.help))
            self.application.add_handler(CommandHandler("status", self.status))

            # Set commands for BotFather menu
            commands = [
                BotCommand("start", "Start the bot"),
                BotCommand("analyze", "Analyze a symbol"),
                BotCommand("help", "Show help"),
                BotCommand("status", "Bot status"),
            ]
            await self.application.bot.set_my_commands(commands)

            # Add error handler
            self.application.add_error_handler(self.error_handler)

            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            raise TelegramError(f"Failed to initialize bot: {e}")

    async def start_polling(self) -> None:
        """
        Start bot polling.

        Raises:
            TelegramError: If polling fails
        """
        try:
            if not self.application:
                await self.initialize()

            logger.info("Starting bot polling...")
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("Bot polling started")
        except Exception as e:
            raise TelegramError(f"Failed to start polling: {e}")

    async def stop(self) -> None:
        """
        Stop the bot.
        """
        if self.application:
            await self.application.stop()
            logger.info("Bot stopped")
