"""
Configuration management.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from src.utils.exceptions import ConfigError


class Config:
    """
    Configuration manager for the bot.
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file

        Raises:
            ConfigError: If configuration file not found or invalid
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """
        Load configuration from YAML file.

        Raises:
            ConfigError: If file not found or invalid YAML
        """
        if not self.config_path.exists():
            raise ConfigError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (supports nested keys with dots)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration."""
        return self.get("telegram", {})

    def get_binance_config(self) -> Dict[str, Any]:
        """Get Binance configuration."""
        return self.get("binance", {})

    def get_market_config(self) -> Dict[str, Any]:
        """Get market configuration."""
        return self.get("market", {})

    def get_indicators_config(self) -> Dict[str, Any]:
        """Get indicators configuration."""
        return self.get("indicators", {})

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.get("database", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get("logging", {})

    def validate(self) -> bool:
        """
        Validate required configuration keys.

        Returns:
            True if valid, raises ConfigError otherwise
        """
        required_keys = ["telegram", "market", "indicators"]

        for key in required_keys:
            if key not in self.config:
                raise ConfigError(f"Missing required configuration: {key}")

        # Validate Telegram config
        telegram = self.get_telegram_config()
        if not telegram.get("bot_token"):
            raise ConfigError("Missing Telegram bot_token")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary."""
        return self.config.copy()
