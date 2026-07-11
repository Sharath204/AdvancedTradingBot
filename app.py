"""
Flask web application for Telegram Market Analysis Bot.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
from src.utils.config import Config
from src.utils.logger import get_logger
from src.data.market_data import MarketData
from src.analysis.multi_timeframe import MultiTimeframeAnalysis
from src.analysis.signal_confidence import SignalConfidence
from src.backtesting.backtest import Backtest
from src.backtesting.strategy import EMACrossoverStrategy, RSIStrategy
from src.data.database import Database

logger = get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize components
try:
    config = Config("config/config.yaml")
    market_data = MarketData(exchange_name="binance", config=config.get_binance_config())
    mta = MultiTimeframeAnalysis(market_data)
    database = Database()
except Exception as e:
    logger.error(f"Initialization error: {e}")


@app.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    API endpoint for market analysis.
    """
    try:
        data = request.json
        symbol = data.get("symbol", "BTC/USDT").upper()

        # Validate symbol
        if "/" not in symbol:
            symbol = f"{symbol}/USDT"

        logger.info(f"Analyzing {symbol}")

        # Multi-timeframe analysis
        analysis = mta.analyze(symbol)
        confidence = SignalConfidence.calculate_confidence(analysis)

        # Get support/resistance
        from src.analysis.support_resistance import SupportResistance
        df = market_data.get_ohlcv(symbol, "1h")
        supports, resistances = SupportResistance.find_support_resistance(df)
        pivot_points = SupportResistance.calculate_pivot_points(df)

        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "trend": analysis.get("trend", {}),
                "setup": analysis.get("setup", {}),
                "confirmation": analysis.get("confirmation", {}),
            },
            "confidence": confidence,
            "support_resistance": {
                "supports": supports,
                "resistances": resistances,
                "pivot_points": pivot_points,
            },
            "status": "success",
        }

        # Log to database
        from src.data.database import TradeLog
        trade_log = TradeLog(
            symbol=symbol,
            timeframe="multi",
            timestamp=datetime.now(),
            signal_type="analysis",
            confidence_score=confidence.get("overall_confidence", 0),
            entry_price=analysis.get("trend", {}).get("current_price", 0),
            exit_price=None,
            pnl=None,
            indicators=json.dumps(analysis),
            analysis_notes="Web analysis",
        )
        database.insert_trade_log(trade_log)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/symbols", methods=["GET"])
def get_symbols():
    """
    Get available symbols.
    """
    try:
        symbols = market_data.get_symbols()
        # Filter to common symbols
        common_symbols = [
            s for s in symbols if any(
                pair in s for pair in ["USDT", "BUSD", "USDC"]
            )
        ][:50]  # Limit to 50

        return jsonify({
            "status": "success",
            "symbols": sorted(common_symbols),
            "total": len(common_symbols),
        })
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/backtest", methods=["POST"])
def backtest():
    """
    API endpoint for backtesting.
    """
    try:
        data = request.json
        symbol = data.get("symbol", "BTC/USDT").upper()
        timeframe = data.get("timeframe", "1h")
        days = data.get("days", 30)
        strategy_name = data.get("strategy", "ema")

        # Select strategy
        if strategy_name == "ema":
            strategy = EMACrossoverStrategy()
        elif strategy_name == "rsi":
            strategy = RSIStrategy()
        else:
            return jsonify({"status": "error", "message": "Unknown strategy"}), 400

        logger.info(f"Running backtest for {symbol} with {strategy.name}")

        # Run backtest
        bt = Backtest(market_data, strategy)
        results = bt.run(symbol, timeframe, days)

        return jsonify({
            "status": "success",
            "results": results,
        })
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/statistics/<symbol>", methods=["GET"])
def get_statistics(symbol):
    """
    Get trading statistics for a symbol.
    """
    try:
        stats = database.get_statistics(symbol)
        return jsonify({
            "status": "success",
            "statistics": stats,
        })
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Get trading history.
    """
    try:
        symbol = request.args.get("symbol")
        limit = int(request.args.get("limit", 100))
        logs = database.get_trade_logs(symbol, limit)

        return jsonify({
            "status": "success",
            "logs": logs,
            "count": len(logs),
        })
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/config", methods=["GET"])
def get_config():
    """
    Get bot configuration (public info only).
    """
    try:
        return jsonify({
            "status": "success",
            "config": {
                "symbols": config.get("market.symbols", []),
                "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
                "update_interval": config.get("market.update_interval", 300),
            },
        })
    except Exception as e:
        logger.error(f"Error fetching config: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Flask web server...")
    app.run(debug=True, host="0.0.0.0", port=5000)
