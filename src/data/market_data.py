"""
Market data fetching module.
Prepared for OTC data source integration.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from src.utils.logger import get_logger
from src.utils.exceptions import MarketDataError

logger = get_logger(__name__)


class MarketData:
    """
    Market data fetcher for OTC analysis.
    """

    def __init__(self):
        self.data_cache: Dict[str, pd.DataFrame] = {}
        logger.info("Initialized OTC MarketData module")

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        limit: int = 100,
        since: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get OHLCV data for OTC symbol.

        Example:
        USDINR-OTC
        EURUSD-OTC
        """

        try:
            cache_key = f"{symbol}_{timeframe}"

            if cache_key in self.data_cache:
                return self.data_cache[cache_key]

            # OTC data source will be added here
            raise MarketDataError(
                f"No OTC candle source configured for {symbol}"
            )

        except Exception as e:
            raise MarketDataError(
                f"Failed to fetch OTC OHLCV data: {e}"
            )

    def get_ticker(self, symbol: str) -> Dict:
        """
        Get current OTC price.
        """

        raise MarketDataError(
            f"Ticker not available for OTC symbol: {symbol}"
        )

    def get_order_book(
        self,
        symbol: str,
        limit: int = 20
    ) -> Tuple[List, List]:
        """
        Order book is not available for OTC.
        """

        raise MarketDataError(
            "Order book is not available for OTC markets"
        )

    def get_symbols(self) -> List[str]:
        """
        Return supported OTC symbols.
        """

        return [
            "USDINR-OTC",
            "USDIDR-OTC",
            "USDPHP-OTC",
            "EURUSD-OTC",
            "GBPUSD-OTC"
        ]

    def get_24h_volume(self, symbol: str) -> float:
        """
        OTC volume is not available.
        """

        return 0.0

    def get_multiple_ohlcv(
        self,
        symbols: List[str],
        timeframe: str = "1m",
        limit: int = 100
    ) -> Dict[str, pd.DataFrame]:

        data = {}

        for symbol in symbols:
            try:
                data[symbol] = self.get_ohlcv(
                    symbol,
                    timeframe,
                    limit
                )

            except MarketDataError as e:
                logger.warning(
                    f"Failed OTC data for {symbol}: {e}"
                )

        return data

    def calculate_rsi(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:

        delta = df["close"].diff()

        gain = (
            delta.where(delta > 0, 0)
            .rolling(window=period)
            .mean()
        )

        loss = (
            -delta.where(delta < 0, 0)
            .rolling(window=period)
            .mean()
        )

        rs = gain / loss

        rsi = 100 - (100 / (1 + rs))

        return rsi

    def clear_cache(
        self,
        symbol: Optional[str] = None
    ):

        if symbol:
            keys = [
                k for k in self.data_cache
                if symbol in k
            ]

            for key in keys:
                del self.data_cache[key]

        else:
            self.data_cache.clear()

        logger.debug("Data cache cleared")