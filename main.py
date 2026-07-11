"""
Main entry point for the Telegram Market Analysis Bot.
"""

import asyncio
import sys
from pathlib import Path
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.bot.telegram_bot import TelegramBot
from src.utils.exceptions import ConfigError, TelegramError

# Setup logging
logger = setup_logger(
    "main",
    level="INFO",
    log_file="logs/bot.log",
)


async def main():
    """
    Main function to run the bot.
    """
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = Config("config/config.yaml")
        config.validate()
        logger.info("Configuration loaded successfully")

        # Initialize bot
        logger.info("Initializing Telegram bot...")
        bot = TelegramBot(config)
        await bot.initialize()

        # Start bot
        logger.info("Starting bot polling...")
        await bot.start_polling()

        # Keep bot running
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()

    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your config/config.yaml file")
        sys.exit(1)
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if "bot" in locals():
            await bot.stop()
        logger.info("Bot stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)

    # Run bot
    asyncio.run(main())
