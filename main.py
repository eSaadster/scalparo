"""
Main orchestrator for the trading system
"""
import backtrader as bt
from data_fetcher import DataFetcher, CustomYahooData
from strategies import get_strategy_class
from report_generator import ReportGenerator


def add_analyzers(cerebro: bt.Cerebro):
    """Add all analyzers to cerebro"""
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='time_return')
    cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='positions')


def run_backtest(config: dict, strategy_class: type, strategy_params: dict = None):
    """Run a backtest with given configuration and strategy"""
    
    # Fetch data
    print(f"Fetching data for {config['symbol']}...")
    df = DataFetcher.fetch_yahoo_data(
        config['symbol'],
        config['interval'],
        config['start_date'],
        config['end_date']
    )
    
    if df.empty:
        raise ValueError("No data fetched. Check symbol, source, or date range.")
    
    # Create Cerebro instance
    cerebro = bt.Cerebro()
    
    # Add strategy with parameters
    if strategy_params:
        cerebro.addstrategy(strategy_class, **strategy_params)
    else:
        cerebro.addstrategy(strategy_class)
    
    # Add data
    data = CustomYahooData(dataname=df)
    cerebro.adddata(data)
    
    # Set broker parameters
    cerebro.broker.set_cash(config['initial_capital'])
    cerebro.broker.setcommission(commission=config['commission'])
    
    # Add analyzers
    add_analyzers(cerebro)
    
    # Run strategy
    print(f"\nStarting backtest with {strategy_class.__name__}...")
    print(f"Initial Portfolio Value: ${cerebro.broker.getvalue():.2f}")
    
    results = cerebro.run()
    
    print(f"Final Portfolio Value: ${cerebro.broker.getvalue():.2f}")
    
    return cerebro, results


def main():
    """Main function to run the trading system"""
    
    # Get configuration (in production, this would come from UI)
    config = DataFetcher.get_user_config()
    
    # Select strategy (in production, this would come from UI)
    strategy_name = 'SMA Crossover'  # Default strategy
    strategy_class = get_strategy_class(strategy_name)
    
    # Strategy parameters (in production, these would come from UI)
    strategy_params = {'sma_period': 15}
    
    # Update config with strategy info
    config['strategy_name'] = strategy_name
    config['strategy_params'] = strategy_params
    
    # Run backtest
    cerebro, results = run_backtest(config, strategy_class, strategy_params)
    
    # Generate report
    report_gen = ReportGenerator(cerebro, results, config)
    report_gen.print_report()
    report_gen.save_report()
    
    # Optional: Plot results
    try:
        cerebro.plot(style='candlestick')
    except Exception as e:
        print(f"Plotting failed: {e}")


if __name__ == "__main__":
    main()