"""
Advanced performance analytics for Scalparo Trading Backtester
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
import backtrader as bt


class PerformanceAnalyzer:
    """Advanced performance analysis and metrics calculation"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def analyze_backtest_results(self, cerebro: bt.Cerebro, results: List, 
                                data: pd.DataFrame) -> Dict:
        """Comprehensive analysis of backtest results"""
        
        if not results:
            return {}
        
        strategy = results[0]
        
        # Extract portfolio values over time
        portfolio_values = self._extract_portfolio_values(cerebro)
        
        # Calculate returns
        returns = self._calculate_returns(portfolio_values)
        
        # Get all analysis components
        analysis = {
            'portfolio_values': portfolio_values,
            'returns': returns,
            'basic_metrics': self._calculate_basic_metrics(portfolio_values, returns),
            'risk_metrics': self._calculate_risk_metrics(returns),
            'trade_metrics': self._calculate_trade_metrics(strategy),
            'time_analysis': self._calculate_time_analysis(returns),
            'distribution_analysis': self._calculate_distribution_analysis(returns),
            'rolling_metrics': self._calculate_rolling_metrics(returns),
            'monthly_analysis': self._calculate_monthly_analysis(returns),
            'correlations': self._calculate_correlation_analysis(returns, data)
        }
        
        return analysis
    
    def _extract_portfolio_values(self, cerebro: bt.Cerebro) -> pd.Series:
        """Extract portfolio values over time"""
        
        # Get portfolio values from cerebro
        values = []
        dates = []
        
        # Try to extract from observers
        if hasattr(cerebro, '_userobs') and cerebro._userobs:
            for observer in cerebro._userobs:
                if hasattr(observer, 'lines') and hasattr(observer.lines, 'value'):
                    values = observer.lines.value.array
                    break
        
        # Fallback: use broker values if available
        if not values and hasattr(cerebro, 'broker'):
            # This is a simplified approach
            initial_value = cerebro.broker.get_cash()
            values = [initial_value]  # Placeholder
        
        # Create date index (simplified)
        if hasattr(cerebro, 'datas') and cerebro.datas:
            data_feed = cerebro.datas[0]
            for i in range(len(values) if values else 1):
                try:
                    dates.append(data_feed.datetime.datetime(i))
                except:
                    dates.append(pd.Timestamp.now())
        
        if not values:
            values = [10000]  # Default value
        if not dates:
            dates = [pd.Timestamp.now()]
        
        return pd.Series(values, index=dates[:len(values)])
    
    def _calculate_returns(self, portfolio_values: pd.Series) -> pd.Series:
        """Calculate portfolio returns"""
        return portfolio_values.pct_change().dropna()
    
    def _calculate_basic_metrics(self, portfolio_values: pd.Series, 
                                returns: pd.Series) -> Dict:
        """Calculate basic performance metrics"""
        
        if len(portfolio_values) < 2:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'final_value': portfolio_values.iloc[-1] if len(portfolio_values) > 0 else 0,
                'initial_value': portfolio_values.iloc[0] if len(portfolio_values) > 0 else 0
            }
        
        initial_value = portfolio_values.iloc[0]
        final_value = portfolio_values.iloc[-1]
        total_return = (final_value / initial_value - 1) * 100
        
        # Calculate annualized return
        days = (portfolio_values.index[-1] - portfolio_values.index[0]).days
        years = max(days / 365.25, 1/365.25)  # Avoid division by zero
        annualized_return = ((final_value / initial_value) ** (1 / years) - 1) * 100
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'final_value': final_value,
            'initial_value': initial_value,
            'total_profit_loss': final_value - initial_value,
            'days_traded': days
        }
    
    def _calculate_risk_metrics(self, returns: pd.Series) -> Dict:
        """Calculate risk-related metrics"""
        
        if len(returns) == 0:
            return {
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'value_at_risk_95': 0,
                'expected_shortfall_95': 0,
                'calmar_ratio': 0
            }
        
        # Annualized volatility
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Sharpe ratio
        excess_returns = returns - (self.risk_free_rate / 252)
        sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Value at Risk and Expected Shortfall (95% confidence)
        var_95 = np.percentile(returns, 5) * 100
        es_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100 if len(returns) > 0 else 0
        
        # Calmar ratio
        annualized_return = returns.mean() * 252 * 100
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'value_at_risk_95': var_95,
            'expected_shortfall_95': es_95,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': self._calculate_sortino_ratio(returns)
        }
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio (only downside volatility)"""
        
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - (self.risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if excess_returns.mean() > 0 else 0
        
        downside_deviation = downside_returns.std() * np.sqrt(252)
        return excess_returns.mean() * np.sqrt(252) / downside_deviation if downside_deviation > 0 else 0
    
    def _calculate_trade_metrics(self, strategy) -> Dict:
        """Calculate trade-specific metrics"""
        
        trade_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'avg_trade_duration': 0
        }
        
        # Extract from trade analyzer if available
        if hasattr(strategy, 'analyzers') and hasattr(strategy.analyzers, 'trades'):
            trades = strategy.analyzers.trades.get_analysis()
            
            if 'total' in trades:
                trade_metrics['total_trades'] = trades['total'].get('total', 0)
                
                # Winning trades
                if 'won' in trades:
                    trade_metrics['winning_trades'] = trades['won'].get('total', 0)
                    trade_metrics['avg_win'] = trades['won'].get('pnl', {}).get('average', 0)
                
                # Losing trades
                if 'lost' in trades:
                    trade_metrics['losing_trades'] = trades['lost'].get('total', 0)
                    trade_metrics['avg_loss'] = trades['lost'].get('pnl', {}).get('average', 0)
                
                # Calculate win rate
                if trade_metrics['total_trades'] > 0:
                    trade_metrics['win_rate'] = (trade_metrics['winning_trades'] / 
                                               trade_metrics['total_trades']) * 100
                
                # Profit factor
                gross_profit = abs(trade_metrics['avg_win'] * trade_metrics['winning_trades'])
                gross_loss = abs(trade_metrics['avg_loss'] * trade_metrics['losing_trades'])
                trade_metrics['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else 0
                
                # Best and worst trades
                if 'pnl' in trades['total']:
                    trade_metrics['best_trade'] = trades['total']['pnl'].get('max', 0)
                    trade_metrics['worst_trade'] = trades['total']['pnl'].get('min', 0)
                
                # Consecutive wins/losses
                if 'streak' in trades:
                    trade_metrics['max_consecutive_wins'] = trades['streak'].get('won', {}).get('longest', 0)
                    trade_metrics['max_consecutive_losses'] = trades['streak'].get('lost', {}).get('longest', 0)
        
        return trade_metrics
    
    def _calculate_time_analysis(self, returns: pd.Series) -> Dict:
        """Calculate time-based analysis"""
        
        if len(returns) == 0:
            return {}
        
        # Group returns by different time periods
        daily_stats = self._calculate_period_stats(returns, 'D')
        weekly_stats = self._calculate_period_stats(returns.resample('W').sum(), 'W')
        monthly_stats = self._calculate_period_stats(returns.resample('M').sum(), 'M')
        
        return {
            'daily': daily_stats,
            'weekly': weekly_stats,
            'monthly': monthly_stats,
            'best_day': returns.max() * 100,
            'worst_day': returns.min() * 100,
            'positive_days': (returns > 0).sum(),
            'negative_days': (returns < 0).sum(),
            'flat_days': (returns == 0).sum()
        }
    
    def _calculate_period_stats(self, returns: pd.Series, period: str) -> Dict:
        """Calculate statistics for a given period"""
        
        if len(returns) == 0:
            return {}
        
        return {
            'mean_return': returns.mean() * 100,
            'std_return': returns.std() * 100,
            'skewness': stats.skew(returns.dropna()),
            'kurtosis': stats.kurtosis(returns.dropna()),
            'min_return': returns.min() * 100,
            'max_return': returns.max() * 100
        }
    
    def _calculate_distribution_analysis(self, returns: pd.Series) -> Dict:
        """Analyze return distribution characteristics"""
        
        if len(returns) == 0:
            return {}
        
        clean_returns = returns.dropna()
        
        # Test for normality
        shapiro_stat, shapiro_p = stats.shapiro(clean_returns[:5000]) if len(clean_returns) <= 5000 else (0, 1)
        
        # Calculate percentiles
        percentiles = {
            '1%': np.percentile(clean_returns, 1) * 100,
            '5%': np.percentile(clean_returns, 5) * 100,
            '25%': np.percentile(clean_returns, 25) * 100,
            '50%': np.percentile(clean_returns, 50) * 100,
            '75%': np.percentile(clean_returns, 75) * 100,
            '95%': np.percentile(clean_returns, 95) * 100,
            '99%': np.percentile(clean_returns, 99) * 100
        }
        
        return {
            'percentiles': percentiles,
            'skewness': stats.skew(clean_returns),
            'kurtosis': stats.kurtosis(clean_returns),
            'shapiro_test': {
                'statistic': shapiro_stat,
                'p_value': shapiro_p,
                'is_normal': shapiro_p > 0.05
            },
            'outliers': self._detect_outliers(clean_returns)
        }
    
    def _detect_outliers(self, returns: pd.Series, method: str = 'iqr') -> Dict:
        """Detect outliers in returns"""
        
        if method == 'iqr':
            Q1 = returns.quantile(0.25)
            Q3 = returns.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = returns[(returns < lower_bound) | (returns > upper_bound)]
            
            return {
                'method': 'IQR',
                'lower_bound': lower_bound * 100,
                'upper_bound': upper_bound * 100,
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(returns)) * 100
            }
        
        return {}
    
    def _calculate_rolling_metrics(self, returns: pd.Series, window: int = 30) -> Dict:
        """Calculate rolling performance metrics"""
        
        if len(returns) < window:
            return {}
        
        rolling_return = returns.rolling(window=window).mean() * 252 * 100
        rolling_volatility = returns.rolling(window=window).std() * np.sqrt(252) * 100
        rolling_sharpe = rolling_return / rolling_volatility
        
        # Rolling maximum drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.rolling(window=window).max()
        rolling_dd = ((cumulative - rolling_max) / rolling_max) * 100
        rolling_max_dd = rolling_dd.rolling(window=window).min()
        
        return {
            'window': window,
            'rolling_return': rolling_return,
            'rolling_volatility': rolling_volatility,
            'rolling_sharpe': rolling_sharpe,
            'rolling_max_drawdown': rolling_max_dd,
            'rolling_return_mean': rolling_return.mean(),
            'rolling_volatility_mean': rolling_volatility.mean(),
            'rolling_sharpe_mean': rolling_sharpe.mean()
        }
    
    def _calculate_monthly_analysis(self, returns: pd.Series) -> Dict:
        """Calculate monthly return analysis"""
        
        if len(returns) == 0:
            return {}
        
        # Resample to monthly
        monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        # Create monthly return matrix
        monthly_matrix = {}
        for date, ret in monthly_returns.items():
            year = date.year
            month = date.month
            if year not in monthly_matrix:
                monthly_matrix[year] = {}
            monthly_matrix[year][month] = ret * 100
        
        # Monthly statistics
        monthly_stats = {
            'best_month': monthly_returns.max() * 100,
            'worst_month': monthly_returns.min() * 100,
            'positive_months': (monthly_returns > 0).sum(),
            'negative_months': (monthly_returns < 0).sum(),
            'avg_monthly_return': monthly_returns.mean() * 100,
            'monthly_volatility': monthly_returns.std() * 100
        }
        
        return {
            'monthly_matrix': monthly_matrix,
            'monthly_stats': monthly_stats,
            'monthly_returns': monthly_returns
        }
    
    def _calculate_correlation_analysis(self, returns: pd.Series, 
                                      market_data: pd.DataFrame) -> Dict:
        """Calculate correlation with market data"""
        
        if len(returns) == 0 or market_data.empty:
            return {}
        
        # Calculate market returns
        market_returns = market_data['Close'].pct_change().dropna()
        
        # Align dates
        common_dates = returns.index.intersection(market_returns.index)
        if len(common_dates) == 0:
            return {}
        
        aligned_strategy = returns.loc[common_dates]
        aligned_market = market_returns.loc[common_dates]
        
        # Calculate correlations
        correlation = aligned_strategy.corr(aligned_market)
        
        # Beta calculation
        covariance = np.cov(aligned_strategy, aligned_market)[0, 1]
        market_variance = np.var(aligned_market)
        beta = covariance / market_variance if market_variance > 0 else 0
        
        # Alpha calculation
        market_return = aligned_market.mean() * 252
        strategy_return = aligned_strategy.mean() * 252
        alpha = strategy_return - (self.risk_free_rate + beta * (market_return - self.risk_free_rate))
        
        return {
            'correlation': correlation,
            'beta': beta,
            'alpha': alpha,
            'r_squared': correlation ** 2,
            'tracking_error': (aligned_strategy - aligned_market).std() * np.sqrt(252) * 100
        }
    
    def calculate_benchmark_comparison(self, strategy_returns: pd.Series, 
                                     benchmark_returns: pd.Series) -> Dict:
        """Compare strategy performance against benchmark"""
        
        # Align the series
        common_dates = strategy_returns.index.intersection(benchmark_returns.index)
        if len(common_dates) == 0:
            return {}
        
        strategy_aligned = strategy_returns.loc[common_dates]
        benchmark_aligned = benchmark_returns.loc[common_dates]
        
        # Calculate excess returns
        excess_returns = strategy_aligned - benchmark_aligned
        
        # Performance metrics
        strategy_total = (1 + strategy_aligned).prod() - 1
        benchmark_total = (1 + benchmark_aligned).prod() - 1
        excess_total = strategy_total - benchmark_total
        
        # Risk metrics
        strategy_vol = strategy_aligned.std() * np.sqrt(252)
        benchmark_vol = benchmark_aligned.std() * np.sqrt(252)
        excess_vol = excess_returns.std() * np.sqrt(252)
        
        # Information ratio
        information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
        
        return {
            'excess_return': excess_total * 100,
            'excess_volatility': (strategy_vol - benchmark_vol) * 100,
            'information_ratio': information_ratio,
            'tracking_error': excess_vol * 100,
            'hit_rate': (excess_returns > 0).mean() * 100,
            'up_capture': self._calculate_capture_ratio(strategy_aligned, benchmark_aligned, up=True),
            'down_capture': self._calculate_capture_ratio(strategy_aligned, benchmark_aligned, up=False)
        }
    
    def _calculate_capture_ratio(self, strategy_returns: pd.Series, 
                                benchmark_returns: pd.Series, up: bool = True) -> float:
        """Calculate up/down capture ratio"""
        
        if up:
            mask = benchmark_returns > 0
        else:
            mask = benchmark_returns < 0
        
        if mask.sum() == 0:
            return 0
        
        strategy_avg = strategy_returns[mask].mean()
        benchmark_avg = benchmark_returns[mask].mean()
        
        return (strategy_avg / benchmark_avg) * 100 if benchmark_avg != 0 else 0