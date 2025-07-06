"""
Benchmark calculation utilities for Scalparo Trading Backtester
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
import yfinance as yf


class BenchmarkCalculator:
    """Calculates benchmark performance for comparison with trading strategies"""
    
    def __init__(self):
        self.benchmark_symbols = {
            'SPY': 'S&P 500 ETF',
            'QQQ': 'Nasdaq 100 ETF', 
            'VTI': 'Total Stock Market ETF',
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum',
            'GLD': 'Gold ETF'
        }
    
    def calculate_buy_and_hold(self, data: pd.DataFrame, initial_capital: float = 10000,
                              commission: float = 0.001) -> Dict:
        """Calculate buy and hold performance for the given data"""
        
        if data.empty:
            return self._empty_result(initial_capital)
        
        # Calculate buy and hold returns
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        
        # Account for commission
        shares_bought = (initial_capital * (1 - commission)) / start_price
        final_value = shares_bought * end_price * (1 - commission)
        
        # Calculate metrics
        total_return = (final_value / initial_capital - 1) * 100
        
        # Calculate daily returns for risk metrics
        daily_returns = data['Close'].pct_change().dropna()
        
        # Time period
        start_date = data.index[0]
        end_date = data.index[-1]
        days = (end_date - start_date).days
        years = max(days / 365.25, 1/365.25)
        
        # Annualized return
        annualized_return = ((final_value / initial_capital) ** (1 / years) - 1) * 100
        
        # Risk metrics
        volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # Calculate drawdown
        cumulative_returns = (1 + daily_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        excess_returns = daily_returns - (risk_free_rate / 252)
        sharpe_ratio = excess_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() > 0 else 0
        
        return {
            'type': 'buy_and_hold',
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'shares_bought': shares_bought,
            'start_price': start_price,
            'end_price': end_price,
            'commission_paid': initial_capital * commission + final_value * commission,
            'returns_series': daily_returns,
            'cumulative_returns': cumulative_returns,
            'drawdown_series': drawdown,
            'period_days': days,
            'period_years': years
        }
    
    def calculate_market_benchmark(self, symbol: str, start_date: str, end_date: str,
                                 initial_capital: float = 10000, commission: float = 0.001) -> Dict:
        """Calculate benchmark performance using a market index"""
        
        try:
            # Download benchmark data
            benchmark_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if benchmark_data.empty:
                return self._empty_result(initial_capital, f"No data available for {symbol}")
            
            # Calculate benchmark performance
            result = self.calculate_buy_and_hold(benchmark_data, initial_capital, commission)
            result['benchmark_symbol'] = symbol
            result['benchmark_name'] = self.benchmark_symbols.get(symbol, symbol)
            
            return result
            
        except Exception as e:
            return self._empty_result(initial_capital, f"Error calculating benchmark: {str(e)}")
    
    def calculate_multiple_benchmarks(self, symbols: list, start_date: str, end_date: str,
                                    initial_capital: float = 10000) -> Dict:
        """Calculate performance for multiple benchmark symbols"""
        
        benchmarks = {}
        
        for symbol in symbols:
            result = self.calculate_market_benchmark(symbol, start_date, end_date, initial_capital)
            if result.get('final_value', 0) > 0:  # Only include successful calculations
                benchmarks[symbol] = result
        
        return benchmarks
    
    def compare_with_strategy(self, strategy_results: Dict, benchmark_results: Dict) -> Dict:
        """Compare strategy performance with benchmark"""
        
        if not strategy_results or not benchmark_results:
            return {}
        
        # Extract key metrics
        strategy_return = strategy_results.get('total_return', 0)
        benchmark_return = benchmark_results.get('total_return', 0)
        
        strategy_sharpe = strategy_results.get('sharpe_ratio', 0)
        benchmark_sharpe = benchmark_results.get('sharpe_ratio', 0)
        
        strategy_vol = strategy_results.get('volatility', 0)
        benchmark_vol = benchmark_results.get('volatility', 0)
        
        strategy_dd = strategy_results.get('max_drawdown', 0)
        benchmark_dd = benchmark_results.get('max_drawdown', 0)
        
        # Calculate relative performance
        excess_return = strategy_return - benchmark_return
        return_ratio = strategy_return / benchmark_return if benchmark_return != 0 else 0
        
        # Risk-adjusted comparisons
        sharpe_difference = strategy_sharpe - benchmark_sharpe
        volatility_ratio = strategy_vol / benchmark_vol if benchmark_vol != 0 else 0
        
        # Information ratio (simplified)
        if 'returns_series' in strategy_results and 'returns_series' in benchmark_results:
            strategy_returns = strategy_results['returns_series']
            benchmark_returns = benchmark_results['returns_series']
            
            # Align the series
            common_dates = strategy_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 0:
                excess_returns = strategy_returns.loc[common_dates] - benchmark_returns.loc[common_dates]
                information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
            else:
                information_ratio = 0
        else:
            information_ratio = 0
        
        # Performance categories
        outperformance = "outperformed" if excess_return > 0 else "underperformed"
        risk_efficiency = "more efficient" if strategy_sharpe > benchmark_sharpe else "less efficient"
        
        return {
            'excess_return': excess_return,
            'return_ratio': return_ratio,
            'sharpe_difference': sharpe_difference,
            'volatility_ratio': volatility_ratio,
            'information_ratio': information_ratio,
            'drawdown_comparison': {
                'strategy_dd': strategy_dd,
                'benchmark_dd': benchmark_dd,
                'difference': strategy_dd - benchmark_dd
            },
            'performance_summary': {
                'return_performance': outperformance,
                'risk_efficiency': risk_efficiency,
                'excess_return_pct': excess_return,
                'risk_adjusted_performance': 'better' if sharpe_difference > 0 else 'worse'
            },
            'metrics_comparison': {
                'strategy': {
                    'return': strategy_return,
                    'volatility': strategy_vol,
                    'sharpe': strategy_sharpe,
                    'max_dd': strategy_dd
                },
                'benchmark': {
                    'return': benchmark_return,
                    'volatility': benchmark_vol,
                    'sharpe': benchmark_sharpe,
                    'max_dd': benchmark_dd
                }
            }
        }
    
    def calculate_efficient_frontier_position(self, strategy_results: Dict, 
                                            benchmark_results: Dict) -> Dict:
        """Calculate where strategy sits relative to efficient frontier"""
        
        if not strategy_results or not benchmark_results:
            return {}
        
        strategy_return = strategy_results.get('annualized_return', 0) / 100
        strategy_vol = strategy_results.get('volatility', 0) / 100
        
        benchmark_return = benchmark_results.get('annualized_return', 0) / 100
        benchmark_vol = benchmark_results.get('volatility', 0) / 100
        
        # Simple two-asset efficient frontier
        correlations = [0.0, 0.3, 0.5, 0.7, 1.0]  # Different correlation assumptions
        frontier_points = []
        
        for corr in correlations:
            # Generate portfolio combinations
            weights = np.linspace(0, 1, 11)
            for w in weights:
                # Portfolio return and risk
                port_return = w * strategy_return + (1 - w) * benchmark_return
                port_variance = (w**2 * strategy_vol**2 + 
                               (1-w)**2 * benchmark_vol**2 + 
                               2 * w * (1-w) * corr * strategy_vol * benchmark_vol)
                port_vol = np.sqrt(port_variance)
                
                frontier_points.append({
                    'return': port_return * 100,
                    'volatility': port_vol * 100,
                    'strategy_weight': w,
                    'correlation': corr
                })
        
        # Find optimal portfolio (max Sharpe ratio)
        risk_free_rate = 0.02
        best_sharpe = -np.inf
        optimal_portfolio = None
        
        for point in frontier_points:
            sharpe = (point['return']/100 - risk_free_rate) / (point['volatility']/100)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                optimal_portfolio = point
        
        return {
            'frontier_points': frontier_points,
            'optimal_portfolio': optimal_portfolio,
            'strategy_position': {
                'return': strategy_return * 100,
                'volatility': strategy_vol * 100,
                'sharpe': strategy_results.get('sharpe_ratio', 0)
            },
            'benchmark_position': {
                'return': benchmark_return * 100,
                'volatility': benchmark_vol * 100,
                'sharpe': benchmark_results.get('sharpe_ratio', 0)
            }
        }
    
    def calculate_rolling_comparison(self, strategy_returns: pd.Series, 
                                   benchmark_returns: pd.Series, window: int = 30) -> Dict:
        """Calculate rolling comparison metrics"""
        
        # Align the series
        common_dates = strategy_returns.index.intersection(benchmark_returns.index)
        if len(common_dates) < window:
            return {}
        
        strategy_aligned = strategy_returns.loc[common_dates]
        benchmark_aligned = benchmark_returns.loc[common_dates]
        
        # Rolling excess returns
        excess_returns = strategy_aligned - benchmark_aligned
        rolling_excess = excess_returns.rolling(window=window).mean() * 252
        
        # Rolling outperformance percentage
        rolling_outperformance = (excess_returns > 0).rolling(window=window).mean() * 100
        
        # Rolling correlation
        rolling_correlation = strategy_aligned.rolling(window=window).corr(benchmark_aligned)
        
        # Rolling beta
        rolling_beta = []
        for i in range(window, len(strategy_aligned)):
            strat_window = strategy_aligned.iloc[i-window:i]
            bench_window = benchmark_aligned.iloc[i-window:i]
            
            covariance = np.cov(strat_window, bench_window)[0, 1]
            variance = np.var(bench_window)
            beta = covariance / variance if variance > 0 else 0
            rolling_beta.append(beta)
        
        rolling_beta = pd.Series(rolling_beta, index=strategy_aligned.index[window:])
        
        return {
            'rolling_excess_return': rolling_excess,
            'rolling_outperformance_pct': rolling_outperformance,
            'rolling_correlation': rolling_correlation,
            'rolling_beta': rolling_beta,
            'avg_excess_return': rolling_excess.mean(),
            'avg_outperformance_pct': rolling_outperformance.mean(),
            'avg_correlation': rolling_correlation.mean(),
            'avg_beta': rolling_beta.mean() if len(rolling_beta) > 0 else 0
        }
    
    def _empty_result(self, initial_capital: float, error_msg: str = "") -> Dict:
        """Return empty result structure"""
        return {
            'type': 'buy_and_hold',
            'initial_capital': initial_capital,
            'final_value': initial_capital,
            'total_return': 0.0,
            'annualized_return': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'error': error_msg if error_msg else "No data available"
        }
    
    def get_appropriate_benchmark(self, symbol: str) -> str:
        """Suggest appropriate benchmark based on trading symbol"""
        
        symbol_upper = symbol.upper()
        
        # Cryptocurrency
        if any(crypto in symbol_upper for crypto in ['BTC', 'ETH', 'CRYPTO']):
            return 'BTC-USD'
        
        # Tech stocks
        if any(tech in symbol_upper for tech in ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'TSLA']):
            return 'QQQ'
        
        # Gold/Commodities
        if any(commodity in symbol_upper for commodity in ['GLD', 'GOLD', 'SLV']):
            return 'GLD'
        
        # Default to S&P 500
        return 'SPY'
    
    def create_benchmark_report(self, strategy_results: Dict, symbol: str, 
                              start_date: str, end_date: str) -> Dict:
        """Create comprehensive benchmark comparison report"""
        
        # Get appropriate benchmark
        benchmark_symbol = self.get_appropriate_benchmark(symbol)
        
        # Calculate benchmark performance
        benchmark_results = self.calculate_market_benchmark(
            benchmark_symbol, start_date, end_date, 
            strategy_results.get('initial_capital', 10000)
        )
        
        # Perform comparison
        comparison = self.compare_with_strategy(strategy_results, benchmark_results)
        
        # Create report
        report = {
            'benchmark_info': {
                'symbol': benchmark_symbol,
                'name': self.benchmark_symbols.get(benchmark_symbol, benchmark_symbol),
                'period': f"{start_date} to {end_date}"
            },
            'benchmark_performance': benchmark_results,
            'comparison_analysis': comparison,
            'summary': self._create_comparison_summary(comparison),
            'recommendations': self._generate_recommendations(comparison)
        }
        
        return report
    
    def _create_comparison_summary(self, comparison: Dict) -> str:
        """Create human-readable summary of comparison"""
        
        if not comparison:
            return "Unable to generate comparison summary."
        
        performance = comparison.get('performance_summary', {})
        excess_return = comparison.get('excess_return', 0)
        sharpe_diff = comparison.get('sharpe_difference', 0)
        
        summary_parts = []
        
        # Return performance
        if excess_return > 5:
            summary_parts.append(f"significantly outperformed the benchmark by {excess_return:.1f}%")
        elif excess_return > 0:
            summary_parts.append(f"outperformed the benchmark by {excess_return:.1f}%")
        elif excess_return > -5:
            summary_parts.append(f"slightly underperformed the benchmark by {abs(excess_return):.1f}%")
        else:
            summary_parts.append(f"significantly underperformed the benchmark by {abs(excess_return):.1f}%")
        
        # Risk-adjusted performance
        if sharpe_diff > 0.2:
            summary_parts.append("with much better risk-adjusted returns")
        elif sharpe_diff > 0:
            summary_parts.append("with better risk-adjusted returns")
        elif sharpe_diff > -0.2:
            summary_parts.append("with similar risk-adjusted returns")
        else:
            summary_parts.append("with worse risk-adjusted returns")
        
        return f"The strategy {' '.join(summary_parts)}."
    
    def _generate_recommendations(self, comparison: Dict) -> List[str]:
        """Generate recommendations based on comparison analysis"""
        
        recommendations = []
        
        if not comparison:
            return ["Unable to generate recommendations due to insufficient data."]
        
        excess_return = comparison.get('excess_return', 0)
        sharpe_diff = comparison.get('sharpe_difference', 0)
        vol_ratio = comparison.get('volatility_ratio', 1)
        
        # Performance recommendations
        if excess_return <= 0:
            recommendations.append("Consider improving strategy returns as it underperformed the benchmark")
        
        if sharpe_diff <= 0:
            recommendations.append("Focus on improving risk-adjusted returns (Sharpe ratio)")
        
        if vol_ratio > 1.5:
            recommendations.append("Strategy has high volatility - consider risk management techniques")
        
        if excess_return > 0 and sharpe_diff > 0:
            recommendations.append("Strategy shows good performance - consider position sizing optimization")
        
        # Always include this general recommendation
        recommendations.append("Consider combining strategy with benchmark allocation for portfolio optimization")
        
        return recommendations