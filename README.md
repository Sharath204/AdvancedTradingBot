# Telegram Market Analysis Bot

A production-quality Python Telegram bot for real-time market analysis with advanced technical indicators, multi-timeframe analysis, and backtesting capabilities.

## Features

### Technical Indicators
- **Moving Averages**: EMA 20/50/200
- **Momentum**: RSI, MACD, ADX
- **Volatility**: ATR, Bollinger Bands
- **Volume**: VWAP
- **Pattern Recognition**: Candlestick patterns
- **Support/Resistance**: Automatic detection

### Analysis Capabilities
- **Multi-Timeframe Analysis**: 15m trend, 5m setup, 1m confirmation
- **Signal Confidence Score**: Weighted scoring system
- **Real-Time Monitoring**: 5-minute scheduler
- **Backtesting Module**: Historical analysis and strategy testing
- **Database Logging**: SQLite for trade history and analysis logs

### Architecture
- Modular, production-ready code
- Clean separation of concerns
- Comprehensive error handling
- Configuration management
- Logging system
- Unit tests

## Requirements

- Python 3.11+
- Telegram Bot Token
- Binance API credentials (optional, for extended data)

## Installation

```bash
# Clone the repository
git clone https://github.com/Sharath204/AdvancedTradingBot.git
cd AdvancedTradingBot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `config/config.example.yaml` to `config/config.yaml`
2. Add your Telegram Bot Token:
```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"
```

3. (Optional) Add Binance credentials for extended data:
```yaml
binance:
  api_key: "YOUR_API_KEY"
  api_secret: "YOUR_API_SECRET"
```

## Usage

```bash
# Start the bot
python main.py

# Run tests
pytest tests/

# Run backtesting
python -m src.backtesting.backtest --symbol BTC/USDT --timeframe 1h --days 30
```

## Project Structure

```
AdvancedTradingBot/
├── config/
│   ├── config.example.yaml
│   └── config.yaml (create from example)
├── src/
│   ├── __init__.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── telegram_bot.py
│   │   └── handlers.py
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── moving_averages.py
│   │   ├── momentum.py
│   │   ├── volatility.py
│   │   ├── volume.py
│   │   └── patterns.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── support_resistance.py
│   │   ├── multi_timeframe.py
│   │   └── signal_confidence.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── market_data.py
│   │   └── database.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── exceptions.py
│   └── backtesting/
│       ├── __init__.py
│       ├── backtest.py
│       └── strategy.py
├── tests/
│   ├── __init__.py
│   ├── test_indicators.py
│   ├── test_analysis.py
│   ├── test_market_data.py
│   └── test_backtesting.py
├── logs/
│   └── .gitkeep
├── data/
│   └── trades.db (SQLite)
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Telegram Commands

Send these commands to the bot via Telegram:

- `/analyze SYMBOL` - Analyze a symbol (e.g., `/analyze BTC/USDT`)
- `/status` - Get current monitoring status
- `/help` - Display help message
- `/settings` - View/update settings

## Architecture Overview

### Bot Layer
- Handles Telegram communications
- Command parsing and routing
- Message formatting and delivery

### Indicators Layer
- Calculates technical indicators
- Handles data normalization
- Caches calculations

### Analysis Layer
- Multi-timeframe analysis
- Support/Resistance detection
- Candlestick pattern recognition
- Confidence score calculation

### Data Layer
- Market data fetching via CCXT
- Database operations
- Data caching

### Utils Layer
- Configuration management
- Logging
- Exception handling
- Custom exceptions

## Error Handling

The bot includes comprehensive error handling for:
- Network errors
- Invalid symbols
- Data inconsistencies
- Database errors
- API failures

All errors are logged and reported appropriately.

## Testing

Run the test suite:

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_indicators.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Performance Considerations

- Efficient data caching
- Async/await for I/O operations
- Database indexing
- Minimal API calls
- Memory optimization for large datasets

## Backtesting

Test strategies on historical data:

```bash
python -m src.backtesting.backtest \
    --symbol BTC/USDT \
    --timeframe 1h \
    --days 90 \
    --strategy ema_crossover
```

## Limitations

- Real-time data depends on exchange API rate limits
- Backtesting based on OHLCV data availability
- Multi-timeframe analysis requires sufficient historical data

## Future Enhancements

- [ ] Machine learning signal generation
- [ ] Portfolio analysis
- [ ] Advanced order management
- [ ] Risk management strategies
- [ ] Multiple exchange support
- [ ] Web dashboard

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please visit the GitHub repository.

---

**Disclaimer**: This bot is for educational and analysis purposes only. Use it at your own risk. Past performance is not indicative of future results. Always conduct your own research before making trading decisions.