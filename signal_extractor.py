"""
Signal extraction utilities for Scalparo Trading Backtester
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import backtrader as bt


class SignalExtractor:
    """Extracts trading signals from backtest results for visualization"""

    def __init__(self):
        self.signals = {
            'buy_signals': {'timestamp': [], 'price': [], 'reason': []},
            'sell_signals': {'timestamp': [], 'price': [], 'reason': []},
            'trades': [],
            'execution_prices': {
                'buy_executions': [],
                'sell_executions': [],
                'average_buy_price': 0,
                'average_sell_price': 0,
                'total_executions': 0
            }
        }

    def extract_from_backtest(self, cerebro: bt.Cerebro, results: List) -> Dict:
        """Extract signals and trades from backtest results"""

        if not results:
            return self.signals

        strategy = results[0]
        
        # Extract execution prices if available
        self._extract_execution_prices(strategy)

        # Extract data safely
        dates = []
        prices = []

        try:
            if cerebro.datas:
                data_feed = cerebro.datas[0]

                # Get the length of available data
                data_len = len(data_feed.close.array)

                # Extract price data safely
                for i in range(data_len):
                    try:
                        # Try to get datetime - handle potential errors
                        if hasattr(data_feed, 'datetime') and hasattr(data_feed.datetime, 'array'):
                            if i < len(data_feed.datetime.array):
                                dates.append(data_feed.datetime.datetime(i))
                            else:
                                # Fallback to index-based date
                                dates.append(f"Period_{i}")
                        else:
                            dates.append(f"Period_{i}")

                        # Get price data
                        if i < len(data_feed.close.array):
                            prices.append(data_feed.close[i])
                        else:
                            prices.append(0.0)

                    except (IndexError, AttributeError) as e:
                        # If we can't get the data, use fallback values
                        dates.append(f"Period_{i}")
                        prices.append(0.0)

        except Exception as e:
            print(f"Warning: Could not extract data from cerebro: {e}")
            # Use minimal fallback data
            dates = ["Period_0"]
            prices = [100.0]

        # Extract trade data from analyzer
        try:
            if hasattr(strategy, 'analyzers') and hasattr(strategy.analyzers, 'trades'):
                trade_analyzer = strategy.analyzers.trades.get_analysis()
                self._extract_trade_data(trade_analyzer, dates, prices)
        except Exception as e:
            print(f"Warning: Could not extract trade data: {e}")

        # Try to extract signals from strategy if it logs them
        try:
            if hasattr(strategy, '_signals') and strategy._signals:
                self._extract_strategy_signals(strategy._signals)
            else:
                # Fallback: try to infer signals from trade data
                self._infer_signals_from_trades(dates, prices)
        except Exception as e:
            print(f"Warning: Could not extract signals: {e}")
            # Create minimal fallback signals
            self._create_fallback_signals(dates, prices)

        return self.signals

    def _extract_trade_data(self, trade_analysis: Dict, dates: List, prices: List) -> None:
        """Extract trade information from backtrader trade analyzer"""

        # Extract basic trade statistics
        if 'total' in trade_analysis:
            total_trades = trade_analysis['total'].get('total', 0)

            # If we have trade details, extract them
            if 'long' in trade_analysis:
                long_trades = trade_analysis['long']
                self._process_trade_direction(long_trades, 'long')

            if 'short' in trade_analysis:
                short_trades = trade_analysis['short'] 
                self._process_trade_direction(short_trades, 'short')

    def _process_trade_direction(self, trade_data: Dict, direction: str) -> None:
        """Process trades for a specific direction (long/short)"""

        if 'total' in trade_data:
            total = trade_data['total'].get('total', 0)
            won = trade_data['won'].get('total', 0) if 'won' in trade_data else 0
            lost = trade_data['lost'].get('total', 0) if 'lost' in trade_data else 0

            # Add trade summary to our signals
            for i in range(total):
                trade_info = {
                    'direction': direction,
                    'result': 'win' if i < won else 'loss',
                    'trade_number': len(self.signals['trades']) + 1
                }

                # Add P&L if available
                if 'pnl' in trade_data and 'total' in trade_data['pnl']:
                    avg_pnl = trade_data['pnl']['total'] / total if total > 0 else 0
                    trade_info['pnl'] = avg_pnl

                self.signals['trades'].append(trade_info)

    def _extract_strategy_signals(self, strategy_signals: List) -> None:
        """Extract signals from strategy that implements signal logging"""

        for signal in strategy_signals:
            signal_type = signal.get('type', '')
            timestamp = signal.get('timestamp')
            price = signal.get('price', 0)
            reason = signal.get('reason', '')

            if signal_type.lower() == 'buy':
                self.signals['buy_signals']['timestamp'].append(timestamp)
                self.signals['buy_signals']['price'].append(price)
                self.signals['buy_signals']['reason'].append(reason)
            elif signal_type.lower() == 'sell':
                self.signals['sell_signals']['timestamp'].append(timestamp)
                self.signals['sell_signals']['price'].append(price)
                self.signals['sell_signals']['reason'].append(reason)

    def _infer_signals_from_trades(self, dates: List, prices: List) -> None:
        """Fallback method to infer signals from trade data when not explicitly logged"""

        # Simple inference: assume trades are evenly distributed
        total_trades = len(self.signals['trades'])
        if total_trades == 0 or len(dates) == 0:
            return

        # Distribute trades across the time period
        interval = max(1, len(dates) // (total_trades * 2))  # *2 for buy and sell

        for i, trade in enumerate(self.signals['trades']):
            # Calculate approximate timestamps for buy/sell signals
            buy_index = min(i * interval * 2, len(dates) - 1)
            sell_index = min((i * interval * 2) + interval, len(dates) - 1)

            # Add buy signal
            self.signals['buy_signals']['timestamp'].append(dates[buy_index])
            self.signals['buy_signals']['price'].append(prices[buy_index])
            self.signals['buy_signals']['reason'].append(f"Trade #{i+1} entry")

            # Add sell signal
            self.signals['sell_signals']['timestamp'].append(dates[sell_index])
            self.signals['sell_signals']['price'].append(prices[sell_index])
            result = "profit" if trade.get('result') == 'win' else "loss"
            self.signals['sell_signals']['reason'].append(f"Trade #{i+1} exit ({result})")

    def format_for_plotting(self, signals: Dict) -> Dict:
        """Format signals for plotting with chart components"""

        formatted = {}

        # Format buy signals
        if signals['buy_signals']['timestamp']:
            formatted['buy_signals'] = pd.DataFrame({
                'timestamp': signals['buy_signals']['timestamp'],
                'price': signals['buy_signals']['price'],
                'reason': signals['buy_signals']['reason']
            })

        # Format sell signals  
        if signals['sell_signals']['timestamp']:
            formatted['sell_signals'] = pd.DataFrame({
                'timestamp': signals['sell_signals']['timestamp'],
                'price': signals['sell_signals']['price'],
                'reason': signals['sell_signals']['reason']
            })

        return formatted

    def get_trade_markers(self, trades: List[Dict]) -> Dict:
        """Get trade markers for visualization"""

        buy_markers = []
        sell_markers = []

        for trade in trades:
            if trade.get('direction') == 'long':
                # Long trade: buy to open, sell to close
                buy_markers.append({
                    'timestamp': trade.get('entry_time'),
                    'price': trade.get('entry_price'),
                    'type': 'buy_to_open'
                })
                sell_markers.append({
                    'timestamp': trade.get('exit_time'),
                    'price': trade.get('exit_price'), 
                    'type': 'sell_to_close'
                })
            elif trade.get('direction') == 'short':
                # Short trade: sell to open, buy to close
                sell_markers.append({
                    'timestamp': trade.get('entry_time'),
                    'price': trade.get('entry_price'),
                    'type': 'sell_to_open'
                })
                buy_markers.append({
                    'timestamp': trade.get('exit_time'),
                    'price': trade.get('exit_price'),
                    'type': 'buy_to_close'
                })

        return {
            'buy_markers': buy_markers,
            'sell_markers': sell_markers
        }

    def calculate_signal_performance(self, signals: Dict, prices: pd.Series) -> Dict:
        """Calculate performance metrics for the signals"""

        performance = {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'signal_frequency': 0,  # signals per day
            'avg_signal_price': 0
        }

        # Count signals
        performance['buy_signals'] = len(signals['buy_signals']['timestamp'])
        performance['sell_signals'] = len(signals['sell_signals']['timestamp'])
        performance['total_signals'] = performance['buy_signals'] + performance['sell_signals']

        # Calculate frequency
        if len(prices) > 0:
            performance['signal_frequency'] = performance['total_signals'] / len(prices)

        # Calculate average signal price
        all_prices = signals['buy_signals']['price'] + signals['sell_signals']['price']
        if all_prices:
            performance['avg_signal_price'] = np.mean(all_prices)

        return performance

    def extract_indicators_from_strategy(self, strategy) -> Dict:
        """Extract technical indicators from strategy for overlay on charts"""

        indicators = {}

        # Common indicator attributes to look for
        indicator_attrs = [
            'sma', 'ema', 'rsi', 'macd', 'bollinger', 'stoch',
            'atr', 'adx', 'cci', 'williams', 'momentum'
        ]

        for attr_name in indicator_attrs:
            if hasattr(strategy, attr_name):
                indicator = getattr(strategy, attr_name)

                # Extract indicator values
                if hasattr(indicator, 'lines') and hasattr(indicator.lines, '__iter__'):
                    # Multi-line indicator (like MACD)
                    for i, line in enumerate(indicator.lines):
                        line_name = getattr(line, '_name', f"{attr_name}_{i}")
                        if hasattr(line, 'array'):
                            values = line.array[~np.isnan(line.array)]
                            if len(values) > 0:
                                indicators[f"{attr_name}_{line_name}"] = pd.Series(values)
                elif hasattr(indicator, 'array'):
                    # Single-line indicator
                    values = indicator.array[~np.isnan(indicator.array)]
                    if len(values) > 0:
                        indicators[attr_name] = pd.Series(values)

        return indicators

    def create_signal_summary(self, signals: Dict) -> Dict:
        """Create a summary of signal analysis"""

        summary = {
            'signal_stats': {
                'total_buy_signals': len(signals['buy_signals']['timestamp']),
                'total_sell_signals': len(signals['sell_signals']['timestamp']),
                'total_trades': len(signals['trades'])
            },
            'trade_stats': {
                'winning_trades': len([t for t in signals['trades'] if t.get('result') == 'win']),
                'losing_trades': len([t for t in signals['trades'] if t.get('result') == 'loss']),
                'win_rate': 0
            }
        }

        # Calculate win rate
        total_trades = summary['trade_stats']['winning_trades'] + summary['trade_stats']['losing_trades']
        if total_trades > 0:
            summary['trade_stats']['win_rate'] = (summary['trade_stats']['winning_trades'] / total_trades) * 100

        # Calculate average P&L
        trade_pnls = [t.get('pnl', 0) for t in signals['trades'] if 'pnl' in t]
        if trade_pnls:
            summary['trade_stats']['avg_pnl'] = np.mean(trade_pnls)
            summary['trade_stats']['total_pnl'] = np.sum(trade_pnls)
        else:
            summary['trade_stats']['avg_pnl'] = 0
            summary['trade_stats']['total_pnl'] = 0

        return summary

    def _create_fallback_signals(self, dates: List, prices: List) -> None:
        """Create minimal fallback signals when extraction fails"""
        if len(dates) > 0 and len(prices) > 0:
            # Create a simple buy signal at the beginning
            self.signals['buy_signals']['timestamp'].append(dates[0])
            self.signals['buy_signals']['price'].append(prices[0])
            self.signals['buy_signals']['reason'].append("Fallback buy signal")

            # Create a simple sell signal at the end if we have more than one data point
            if len(dates) > 1:
                self.signals['sell_signals']['timestamp'].append(dates[-1])
                self.signals['sell_signals']['price'].append(prices[-1])
                self.signals['sell_signals']['reason'].append("Fallback sell signal")

    def _extract_execution_prices(self, strategy) -> None:
        """Extract execution prices from strategy order history"""
        buy_executions = []
        sell_executions = []
        
        # Try to get execution data from strategy if it has logged orders
        if hasattr(strategy, '_execution_log'):
            for execution in strategy._execution_log:
                if execution['side'] == 'buy':
                    buy_executions.append(execution['price'])
                elif execution['side'] == 'sell':
                    sell_executions.append(execution['price'])
        else:
            # Fallback: try to extract from signals if available
            if hasattr(strategy, '_signals') and strategy._signals:
                for signal in strategy._signals:
                    if signal.get('type', '').lower() == 'buy':
                        buy_executions.append(signal.get('price', 0))
                    elif signal.get('type', '').lower() == 'sell':
                        sell_executions.append(signal.get('price', 0))
        
        # Store execution prices
        self.signals['execution_prices']['buy_executions'] = buy_executions
        self.signals['execution_prices']['sell_executions'] = sell_executions
        self.signals['execution_prices']['total_executions'] = len(buy_executions) + len(sell_executions)
        
        # Calculate averages
        if buy_executions:
            self.signals['execution_prices']['average_buy_price'] = sum(buy_executions) / len(buy_executions)
        if sell_executions:
            self.signals['execution_prices']['average_sell_price'] = sum(sell_executions) / len(sell_executions)


class StrategySignalLogger:
    """Mixin class for strategies to log signals during execution"""

    def __init__(self):
        self._signals = []

    def log_signal(self, signal_type: str, price: float, reason: str = "", timestamp=None):
        """Log a trading signal"""

        if timestamp is None:
            timestamp = self.datetime.datetime()

        signal = {
            'type': signal_type,
            'timestamp': timestamp,
            'price': price,
            'reason': reason
        }

        self._signals.append(signal)

    def log_buy_signal(self, price: float, reason: str = ""):
        """Log a buy signal"""
        self.log_signal('buy', price, reason)

    def log_sell_signal(self, price: float, reason: str = ""):
        """Log a sell signal"""
        self.log_signal('sell', price, reason)

    def get_signals(self) -> List[Dict]:
        """Get all logged signals"""
        return self._signals.copy()