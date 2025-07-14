# Scalparo - Modular Trading Strategy Backtester

A plug-and-play trading strategy backtesting platform with AI-powered insights.

## Features

- **Modular Architecture**: Clean separation between data fetching, strategy execution, and report generation
- **Plug-and-Play Strategies**: Easy to add, remove, and switch between strategies via UI
- **AI-Powered Reports**: Comprehensive performance analysis with intelligent insights
- **Streamlit UI**: User-friendly interface for strategy selection and parameter tuning
- **Custom Strategy Support**: Create and load your own trading strategies

## Project Structure

```
scalparo/
├── data_fetcher.py      # Data input/fetching module
├── strategies.py        # Built-in trading strategies
├── report_generator.py  # AI-powered report generation
├── strategy_manager.py  # Dynamic strategy loading
├── main.py             # Command-line interface
├── app.py              # Streamlit web interface
└── custom_strategies/  # Directory for custom strategies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/scalparo.git
cd scalparo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

Run the Streamlit app:
```bash
streamlit run app.py
```

Features:
- Select from built-in strategies (SMA, RSI, MACD, Bollinger Bands)
- Adjust strategy parameters via UI
- Configure data source and trading settings
- View comprehensive performance reports
- Download results as JSON

### Command Line Interface

Run backtests from the command line:
```bash
python main.py
```
You can provide multiple symbols when prompted. Separate them with commas to run
batch backtests:
```bash
# Example input when prompted for symbols
BTC-USD, ETH-USD, AAPL
```

## Creating Custom Strategies

1. Use the UI to generate a strategy template
2. Edit the generated file in `custom_strategies/`
3. Implement your logic in `should_buy()` and `should_sell()` methods
4. Restart the app to load your strategy

Example custom strategy:
```python
class MyCustomStrategy(BaseStrategy):
    def _initialize_indicators(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def should_buy(self):
        return self.data.close[0] > self.sma[0]
    
    def should_sell(self):
        return self.data.close[0] < self.sma[0]
```

## Built-in Strategies

1. **SMA Crossover**: Buy/sell based on price crossing simple moving average
2. **RSI**: Trade on overbought/oversold conditions
3. **MACD**: Trade on MACD/signal line crossovers
4. **Bollinger Bands**: Trade when price touches bands
5. **Fibonacci Retracement**: Trade on bounces from key Fibonacci levels
6. **Simple**: ATR-based entries with fixed profit target

## Performance Metrics

- Total return and profit/loss
- Sharpe ratio and maximum drawdown
- Win rate and trade statistics
- System quality metrics (SQN, VWR)
- AI-generated insights and recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Submit a pull request

## License

MIT License