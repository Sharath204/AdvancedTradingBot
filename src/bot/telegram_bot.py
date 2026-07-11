"""
Telegram bot main class.
"""

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from src.utils.logger import get_logger
from src.utils.config import Config
from src.data.market_data import MarketData
from src.bot.handlers import CommandHandlers
from src.utils.exceptions import TelegramError

logger = get_logger(__name__)


class TelegramBot:
    """
    Telegram bot main class.
    """

    def __init__(self, config: Config):
        self.config = config
        self.telegram_config = config.get_telegram_config()

        self.market_data = MarketData(
            exchange_name="binance",
            config=config.get_binance_config(),
        )

        self.handlers = CommandHandlers(self.market_data)
        self.application: Application | None = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = """
🤖 *Welcome to Market Analysis Bot!*

I can analyze cryptocurrency markets in real-time.

Commands:
/help
/analyze BTC/USDT
/status
"""
        await update.message.reply_text(
            welcome_message,
            parse_mode="Markdown",
        )

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a symbol.\nExample: /analyze BTC/USDT"
            )
            return

        symbol = context.args[0].upper()

        if "/" not in symbol:
            symbol = f"{symbol}/USDT"

        try:
            await update.message.reply_text(f"📊 Analyzing {symbol}...")

            result = await self.handlers.handle_analyze(symbol)

            await update.message.reply_text(
                result,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.exception(e)
            await update.message.reply_text(
                f"❌ Error analyzing {symbol}"
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await self.handlers.handle_help()
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await self.handlers.handle_status()
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.exception(context.error)

        if isinstance(update, Update) and update.message:
            await update.message.reply_text(
                "❌ Something went wrong."
            )

    async def initialize(self):
        try:
            token = self.telegram_config.get("bot_token")

            if not token:
                raise TelegramError("Bot token not configured")

            self.application = (
                Application.builder()
                .token(token)
                .build()
            )

            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("help", self.help))
            self.application.add_handler(CommandHandler("status", self.status))
            self.application.add_handler(CommandHandler("analyze", self.analyze))

            self.application.add_error_handler(self.error_handler)

            logger.info("Telegram application created")

        except Exception as e:
            raise TelegramError(f"Failed to initialize bot: {e}")

    async def start_polling(self):
        try:
            if self.application is None:
                await self.initialize()

            logger.info("Initializing application...")

            await self.application.initialize()

            commands = [
                BotCommand("start", "Start bot"),
                BotCommand("help", "Help"),
                BotCommand("status", "Status"),
                BotCommand("analyze", "Analyze market"),
            ]

            await self.application.bot.set_my_commands(commands)

            logger.info("Starting application...")

            await self.application.start()

            await self.application.updater.start_polling()

            logger.info("Bot started successfully")

        except Exception as e:
            raise TelegramError(f"Failed to start polling: {e}")

    async def stop(self):
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

            logger.info("Bot stopped")