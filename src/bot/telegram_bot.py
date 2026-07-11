"""
Telegram bot main class.
"""

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
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

        # No Binance
        self.market_data = MarketData()

        self.handlers = CommandHandlers(
            self.market_data
        )

        self.application = None



    async def start(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        message = """
🤖 *Welcome to OTC Signal Bot*

Get market analysis signals.

Commands:

/analyze - Select OTC pair
/status - Bot status
/help - Help
"""

        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )



    async def analyze(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        pairs = self.handlers.get_otc_pairs()

        keyboard = []

        row = []

        for index, pair in enumerate(pairs, start=1):

            row.append(
                InlineKeyboardButton(
                    pair,
                    callback_data=f"analyze_{pair}"
                )
            )

            # 2 buttons per row
            if index % 2 == 0:
                keyboard.append(row)
                row = []


        if row:
            keyboard.append(row)


        reply_markup = InlineKeyboardMarkup(
            keyboard
        )


        await update.message.reply_text(
            "📊 Select OTC Pair:",
            reply_markup=reply_markup
        )



    async def otc_pair_selected(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        query = update.callback_query

        await query.answer()


        if not query.data.startswith(
            "analyze_"
        ):
            return


        symbol = query.data.replace(
            "analyze_",
            ""
        )


        await query.edit_message_text(
            f"⏳ Analyzing {symbol}..."
        )


        try:

            result = await self.handlers.handle_analyze(
                symbol
            )


            await query.message.reply_text(
                result,
                parse_mode="Markdown"
            )


        except Exception as e:

            logger.exception(e)

            await query.message.reply_text(
                f"❌ Error analyzing {symbol}\n{e}"
            )



    async def help(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        message = await self.handlers.handle_help()

        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )



    async def status(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):

        message = await self.handlers.handle_status()

        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )



    async def error_handler(
        self,
        update: object,
        context: ContextTypes.DEFAULT_TYPE
    ):

        logger.exception(
            context.error
        )


        if isinstance(update, Update) and update.message:

            await update.message.reply_text(
                "❌ Something went wrong."
            )



    async def initialize(self):

        try:

            token = self.telegram_config.get(
                "bot_token"
            )


            if not token:

                raise TelegramError(
                    "Telegram bot token missing"
                )


            self.application = (
                Application.builder()
                .token(token)
                .build()
            )


            self.application.add_handler(
                CommandHandler(
                    "start",
                    self.start
                )
            )


            self.application.add_handler(
                CommandHandler(
                    "help",
                    self.help
                )
            )


            self.application.add_handler(
                CommandHandler(
                    "status",
                    self.status
                )
            )


            self.application.add_handler(
                CommandHandler(
                    "analyze",
                    self.analyze
                )
            )


            self.application.add_handler(
                CallbackQueryHandler(
                    self.otc_pair_selected,
                    pattern="^analyze_"
                )
            )


            self.application.add_error_handler(
                self.error_handler
            )


            logger.info(
                "Telegram application initialized"
            )


        except Exception as e:

            raise TelegramError(
                f"Failed to initialize bot: {e}"
            )



    async def start_polling(self):

        try:

            if self.application is None:

                await self.initialize()


            await self.application.initialize()


            commands = [
                BotCommand(
                    "start",
                    "Start bot"
                ),
                BotCommand(
                    "help",
                    "Help"
                ),
                BotCommand(
                    "status",
                    "Status"
                ),
                BotCommand(
                    "analyze",
                    "Select OTC pair"
                ),
            ]


            await self.application.bot.set_my_commands(
                commands
            )


            await self.application.start()

            await self.application.updater.start_polling()


            logger.info(
                "Bot started successfully"
            )


        except Exception as e:

            raise TelegramError(
                f"Failed to start polling: {e}"
            )



    async def stop(self):

        if self.application:

            await self.application.updater.stop()

            await self.application.stop()

            await self.application.shutdown()


            logger.info(
                "Bot stopped"
            )