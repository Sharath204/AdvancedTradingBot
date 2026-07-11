"""
Market data fetching using Yahoo Finance.
Used for forex candle analysis.
"""

import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional, Tuple

from src.utils.logger import get_logger
from src.utils.exceptions import MarketDataError

logger = get_logger(__name__)


class MarketData:
    """
    Market data provider for forex analysis.
    """

    SYMBOL_MAP = {
        "USDINR-OTC": "USDINR=X",
        "EURUSD-OTC": "EURUSD=X",
        "GBPUSD-OTC": "GBPUSD=X",
        "USDJPY-OTC": "JPY=X",
        "AUDUSD-OTC": "AUDUSD=X",
        "USDCAD-OTC": "CAD=X",
        "USDCHF-OTC": "CHF=X",
    }


    def __init__(self):
        self.data_cache = {}

        logger.info(
            "Initialized Forex Market Data"
        )


    def convert_symbol(self, symbol: str):

        if symbol in self.SYMBOL_MAP:
            return self.SYMBOL_MAP[symbol]

        return symbol



    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        limit: int = 100,
        since: Optional[int] = None,
    ) -> pd.DataFrame:

        try:

            yahoo_symbol = self.convert_symbol(symbol)


            interval_map = {
                "1m": "1m",
                "5m": "5m",
                "15m": "15m",
                "1h": "1h"
            }


            interval = interval_map.get(
                timeframe,
                "1m"
            )


            data = yf.download(
                yahoo_symbol,
                period="5d",
                interval=interval,
                progress=False
            )


            if data.empty:
                raise MarketDataError(
                    f"No data found for {symbol}"
                )


            data.reset_index(inplace=True)


            df = pd.DataFrame()

            df["timestamp"] = data["Datetime"]
            df["open"] = data["Open"]
            df["high"] = data["High"]
            df["low"] = data["Low"]
            df["close"] = data["Close"]
            

            df = df.tail(limit)


            df.set_index(
                "timestamp",
                inplace=True
            )


            self.data_cache[
                f"{symbol}_{timeframe}"
            ] = df


            return df


        except Exception as e:

            logger.error(
                f"Market data error: {e}"
            )

            raise MarketDataError(
                str(e)
            )



    def get_symbols(self) -> List[str]:

        return list(
            self.SYMBOL_MAP.keys()
        )



    def get_ticker(
        self,
        symbol: str
    ) -> Dict:

        df = self.get_ohlcv(
            symbol,
            "1m",
            2
        )

        last = df.iloc[-1]


        return {
            "last": float(last["close"])
        }



    def get_multiple_ohlcv(
        self,
        symbols: List[str],
        timeframe="1m",
        limit=100
    ):

        result = {}

        for symbol in symbols:

            try:
                result[symbol] = self.get_ohlcv(
                    symbol,
                    timeframe,
                    limit
                )

            except Exception as e:

                logger.warning(
                    f"{symbol}: {e}"
                )

        return result



    def calculate_rsi(
        self,
        df: pd.DataFrame,
        period=14
    ):

        delta = df["close"].diff()

        gain = (
            delta.where(delta > 0,0)
            .rolling(period)
            .mean()
        )

        loss = (
            -delta.where(delta < 0,0)
            .rolling(period)
            .mean()
        )

        rs = gain / loss

        return 100 - (
            100/(1+rs)
        )