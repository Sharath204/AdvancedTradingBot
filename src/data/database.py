"""
SQLite database management.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseError

logger = get_logger(__name__)


@dataclass
class TradeLog:
    """
    Trade log data class.
    """
    symbol: str
    timeframe: str
    timestamp: datetime
    signal_type: str  # buy, sell, hold
    confidence_score: float
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float]
    indicators: Dict[str, Any]
    analysis_notes: Optional[str] = None


class Database:
    """
    SQLite database manager for trade logs and analysis.
    """

    def __init__(self, db_path: str = "data/trades.db"):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
        self._init_connection()
        self._create_tables()

    def _init_connection(self) -> None:
        """
        Initialize database connection.
        """
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Database connection established: {self.db_path}")
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}")

    def _create_tables(self) -> None:
        """
        Create database tables if they don't exist.
        """
        try:
            cursor = self.connection.cursor()

            # Trade logs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trade_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    signal_type TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    pnl REAL,
                    indicators TEXT NOT NULL,
                    analysis_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create indices for faster queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_symbol ON trade_logs(symbol)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON trade_logs(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_signal ON trade_logs(signal_type)"
            )

            # Analysis cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    analysis_data TEXT NOT NULL,
                    ttl DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_symbol ON analysis_cache(symbol)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_ttl ON analysis_cache(ttl)"
            )

            self.connection.commit()
            logger.info("Database tables created successfully")
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create tables: {e}")

    def insert_trade_log(self, trade_log: TradeLog) -> int:
        """
        Insert trade log into database.

        Args:
            trade_log: TradeLog instance

        Returns:
            Row ID of inserted record
        """
        try:
            import json

            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO trade_logs (
                    symbol, timeframe, timestamp, signal_type, confidence_score,
                    entry_price, exit_price, pnl, indicators, analysis_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trade_log.symbol,
                    trade_log.timeframe,
                    trade_log.timestamp,
                    trade_log.signal_type,
                    trade_log.confidence_score,
                    trade_log.entry_price,
                    trade_log.exit_price,
                    trade_log.pnl,
                    json.dumps(trade_log.indicators),
                    trade_log.analysis_notes,
                ),
            )
            self.connection.commit()
            logger.debug(f"Trade log inserted for {trade_log.symbol}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to insert trade log: {e}")

    def get_trade_logs(
        self, symbol: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trade logs from database.

        Args:
            symbol: Filter by symbol (optional)
            limit: Maximum number of records to return

        Returns:
            List of trade logs
        """
        try:
            cursor = self.connection.cursor()
            if symbol:
                cursor.execute(
                    """
                    SELECT * FROM trade_logs
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (symbol, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM trade_logs
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch trade logs: {e}")

    def get_statistics(self, symbol: str) -> Dict[str, Any]:
        """
        Get trading statistics for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Statistics dictionary
        """
        try:
            cursor = self.connection.cursor()

            # Total trades
            cursor.execute(
                "SELECT COUNT(*) as total FROM trade_logs WHERE symbol = ?",
                (symbol,),
            )
            total = cursor.fetchone()["total"]

            # Winning trades
            cursor.execute(
                "SELECT COUNT(*) as wins FROM trade_logs WHERE symbol = ? AND pnl > 0",
                (symbol,),
            )
            wins = cursor.fetchone()["wins"]

            # Total PnL
            cursor.execute(
                "SELECT SUM(pnl) as total_pnl FROM trade_logs WHERE symbol = ?",
                (symbol,),
            )
            total_pnl = cursor.fetchone()["total_pnl"] or 0

            # Average confidence
            cursor.execute(
                "SELECT AVG(confidence_score) as avg_conf FROM trade_logs WHERE symbol = ?",
                (symbol,),
            )
            avg_conf = cursor.fetchone()["avg_conf"] or 0

            win_rate = (wins / total * 100) if total > 0 else 0

            return {
                "total_trades": total,
                "winning_trades": wins,
                "losing_trades": total - wins,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_pnl, 2),
                "avg_confidence": round(avg_conf, 2),
            }
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get statistics: {e}")

    def close(self) -> None:
        """
        Close database connection.
        """
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
