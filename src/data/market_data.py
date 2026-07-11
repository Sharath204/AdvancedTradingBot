"""
Market data fetching via CCXT.
"""


import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.exceptions import MarketDataError

logger = get_logger(__name__)


class MarketData:
    """
    Market data fetcher using CCXT.
    """

    def __init__(self, exchange_name: str = "binance", config: Optional[Dict] = None):
        """
        Initialize market data fetcher.

        Args:
            exchange_name: Exchange name (binance, kraken, etc.)
            config: Exchange configuration (api_key, api_secret, etc.)
        """
        self.exchange_name = exchange_name
        self.config = config or {}
        self.exchange = self._init_exchange()
        self.data_cache: Dict[str, pd.DataFrame] = {}

    def _init_exchange(self) -> ccxt.Exchange:
        """
        Initialize CCXT exchange.

        Returns:
            CCXT exchange instance

        Raises:
            MarketDataError: If exchange initialization fails
        """
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class(self.config)
            logger.info(f"Initialized {self.exchange_name} exchange")
            return exchange
        except AttributeError:
            raise MarketDataError(f"Unknown exchange: {self.exchange_name}")
        except Exception as e:
            raise MarketDataError(f"Failed to initialize exchange: {e}")

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
        since: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get OHLCV data for a symbol.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch
            since: Starting timestamp in milliseconds

        Returns:
            DataFrame with OHLCV data

        Raises:
            MarketDataError: If data fetch fails
        """
        cache_key = f"{symbol}_{timeframe}"

        try:
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, timeframe, since=since, limit=limit
            )

            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df = df.astype(
                {"open": float, "high": float, "low": float, "close": float, "volume": float}
            )

            self.data_cache[cache_key] = df
            logger.debug(f"Fetched {len(df)} candles for {symbol} {timeframe}")
            return df
        except ccxt.NetworkError as e:
            raise MarketDataError(f"Network error fetching data: {e}")
        except ccxt.ExchangeError as e:
            raise MarketDataError(f"Exchange error: {e}")
        except Exception as e:
            raise MarketDataError(f"Failed to fetch OHLCV data: {e}")

    def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker information.

        Args:
            symbol: Trading pair

        Returns:
            Ticker data dictionary

        Raises:
            MarketDataError: If ticker fetch fails
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.debug(f"Fetched ticker for {symbol}")
            return ticker
        except Exception as e:
            raise MarketDataError(f"Failed to fetch ticker: {e}")

    def get_order_book(
        self, symbol: str, limit: int = 20
    ) -> Tuple[List, List]:
        """
        Get order book (bids and asks).

        Args:
            symbol: Trading pair
            limit: Order book depth

        Returns:
            Tuple of (bids, asks)

        Raises:
            MarketDataError: If order book fetch fails
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            logger.debug(f"Fetched order book for {symbol}")
            return orderbook["bids"], orderbook["asks"]
        except Exception as e:
            raise MarketDataError(f"Failed to fetch order book: {e}")

    def get_symbols(self) -> List[str]:
        """
        Get list of available symbols.

        Returns:
            List of symbols
        """
        try:
            symbols = self.exchange.symbols
            logger.debug(f"Fetched {len(symbols)} symbols from {self.exchange_name}")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return []

    def get_24h_volume(self, symbol: str) -> float:
        """
        Get 24-hour trading volume.

        Args:
            symbol: Trading pair

        Returns:
            Volume in quote currency
        """
        try:
            ticker = self.get_ticker(symbol)
            return ticker.get("quoteVolume", 0)
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return 0

    def get_multiple_ohlcv(
        self, symbols: List[str], timeframe: str = "1h", limit: int = 100
    ) -> Dict[str, pd.DataFrame]:
        """
        Get OHLCV data for multiple symbols.

        Args:
            symbols: List of trading pairs
            timeframe: Timeframe
            limit: Number of candles per symbol

        Returns:
            Dictionary of DataFrames keyed by symbol
        """
        data = {}
        for symbol in symbols:
            try:
                data[symbol] = self.get_ohlcv(symbol, timeframe, limit)
            except MarketDataError as e:
                logger.warning(f"Failed to fetch data for {symbol}: {e}")

        return data

    def calculate_rsi(
        self, df: pd.DataFrame, period: int = 14
    ) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            df: OHLCV DataFrame
            period: RSI period

        Returns:
            RSI values
        """
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def clear_cache(self, symbol: Optional[str] = None) -> None:
        """
        Clear data cache.

        Args:
            symbol: Clear cache for specific symbol (optional)
        """
        if symbol:
            keys_to_remove = [k for k in self.data_cache if symbol in k]
            for key in keys_to_remove:
                del self.data_cache[key]
        else:
            self.data_cache.clear()
        logger.debug("Data cache cleared")
