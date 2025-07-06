"""
Report Generator Module
Generates comprehensive trading reports with AI insights
"""
import json
from typing import Dict, Any, List
from datetime import datetime
import backtrader as bt


class ReportGenerator:
    """Generates comprehensive trading reports"""
    
    def __init__(self, cerebro: bt.Cerebro, results: List, config: Dict[str, Any]):
        self.cerebro = cerebro
        self.results = results
        self.config = config
        self.strat = results[0] if results else None
    
    def generate_performance_metrics(self) -> Dict[str, Any]:
        """Extract performance metrics from backtest results"""
        metrics = {}
        
        # Basic Performance
        starting_value = self.config['initial_capital']
        final_value = self.cerebro.broker.getvalue()
        total_return = (final_value - starting_value) / starting_value * 100
        
        metrics['basic_performance'] = {
            'starting_value': starting_value,
            'final_value': final_value,
            'total_return': total_return,
            'total_profit_loss': final_value - starting_value,
            'strategy_params': self.config.get('strategy_params', {}),
            'data_period': f"{self.config['start_date']} to {self.config['end_date']}",
            'interval': self.config['interval']
        }
        
        if self.strat:
            # Returns Analysis
            returns_analysis = self.strat.analyzers.returns.get_analysis()
            metrics['returns'] = {
                'total_return': returns_analysis.get('rtot', 0),
                'average_return': returns_analysis.get('ravg', 0),
                'annual_return': returns_analysis.get('rnorm', 0),
                'annualized_return': returns_analysis.get('rnorm100', 0)
            }
            
            # Risk Metrics
            sharpe_analysis = self.strat.analyzers.sharpe.get_analysis()
            drawdown_analysis = self.strat.analyzers.drawdown.get_analysis()
            metrics['risk'] = {
                'sharpe_ratio': sharpe_analysis.get('sharperatio', 'N/A'),
                'max_drawdown': drawdown_analysis.get('max', {}).get('drawdown', 0),
                'max_drawdown_period': drawdown_analysis.get('max', {}).get('len', 0),
                'max_drawdown_money': drawdown_analysis.get('max', {}).get('moneydown', 0)
            }
            
            # Trade Analysis
            trades_analysis = self.strat.analyzers.trades.get_analysis()
            total_closed = trades_analysis.get('total', {}).get('closed', 0)
            
            metrics['trades'] = {
                'total_trades': trades_analysis.get('total', {}).get('total', 0),
                'open_trades': trades_analysis.get('total', {}).get('open', 0),
                'closed_trades': total_closed,
                'winning_trades': trades_analysis.get('won', {}).get('total', 0),
                'losing_trades': trades_analysis.get('lost', {}).get('total', 0),
                'win_rate': 0 if total_closed == 0 else 
                           trades_analysis.get('won', {}).get('total', 0) / total_closed * 100,
                'avg_win': trades_analysis.get('won', {}).get('pnl', {}).get('average', 0),
                'avg_loss': trades_analysis.get('lost', {}).get('pnl', {}).get('average', 0),
                'best_trade': trades_analysis.get('won', {}).get('pnl', {}).get('max', 0),
                'worst_trade': trades_analysis.get('lost', {}).get('pnl', {}).get('max', 0),
                'max_consecutive_wins': trades_analysis.get('streak', {}).get('won', {}).get('longest', 0),
                'max_consecutive_losses': trades_analysis.get('streak', {}).get('lost', {}).get('longest', 0)
            }
            
            # System Quality
            sqn_analysis = self.strat.analyzers.sqn.get_analysis()
            vwr_analysis = self.strat.analyzers.vwr.get_analysis()
            metrics['system_quality'] = {
                'sqn': sqn_analysis.get('sqn', 'N/A'),
                'sqn_trades': sqn_analysis.get('trades', 'N/A'),
                'vwr': vwr_analysis.get('vwr', 'N/A')
            }
        
        return metrics
    
    def generate_ai_insights(self, metrics: Dict[str, Any]) -> str:
        """Generate AI-powered insights from the metrics"""
        # This is a placeholder for AI integration
        # In production, this would call an AI API (OpenAI, Claude, etc.)
        
        insights = []
        
        # Performance insights
        total_return = metrics['basic_performance']['total_return']
        if total_return > 0:
            insights.append(f"✅ The strategy generated a positive return of {total_return:.2f}%")
        else:
            insights.append(f"⚠️ The strategy resulted in a loss of {abs(total_return):.2f}%")
        
        # Risk insights
        if 'risk' in metrics:
            sharpe = metrics['risk']['sharpe_ratio']
            if isinstance(sharpe, (int, float)) and sharpe > 1:
                insights.append(f"📊 Good risk-adjusted returns with Sharpe ratio of {sharpe:.2f}")
            
            max_dd = metrics['risk']['max_drawdown']
            if max_dd > 20:
                insights.append(f"⚠️ High maximum drawdown of {max_dd:.2f}% indicates significant risk")
        
        # Trade insights
        if 'trades' in metrics:
            win_rate = metrics['trades']['win_rate']
            if win_rate > 60:
                insights.append(f"🎯 Strong win rate of {win_rate:.2f}%")
            elif win_rate < 40:
                insights.append(f"📉 Low win rate of {win_rate:.2f}% needs improvement")
            
            if metrics['trades']['total_trades'] < 10:
                insights.append("⚠️ Low number of trades may not be statistically significant")
        
        return "\n".join(insights)
    
    def generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate strategy recommendations"""
        recommendations = []
        
        # Based on performance
        if metrics['basic_performance']['total_return'] < 0:
            recommendations.append("Consider adjusting strategy parameters or trying a different strategy")
        
        # Based on risk
        if 'risk' in metrics and metrics['risk']['max_drawdown'] > 25:
            recommendations.append("Implement stop-loss mechanisms to reduce maximum drawdown")
        
        # Based on trades
        if 'trades' in metrics:
            if metrics['trades']['win_rate'] < 50:
                recommendations.append("Review entry conditions to improve win rate")
            if metrics['trades']['total_trades'] < 5:
                recommendations.append("Strategy may be too conservative - consider loosening entry conditions")
        
        return recommendations
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate complete trading report"""
        metrics = self.generate_performance_metrics()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'configuration': self.config,
            'metrics': metrics,
            'ai_insights': self.generate_ai_insights(metrics),
            'recommendations': self.generate_recommendations(metrics),
            'summary': self._generate_summary(metrics)
        }
        
        return report
    
    def _generate_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        return {
            'total_return': f"{metrics['basic_performance']['total_return']:.2f}%",
            'final_value': f"${metrics['basic_performance']['final_value']:,.2f}",
            'total_trades': metrics.get('trades', {}).get('total_trades', 0),
            'win_rate': f"{metrics.get('trades', {}).get('win_rate', 0):.2f}%",
            'sharpe_ratio': metrics.get('risk', {}).get('sharpe_ratio', 'N/A'),
            'max_drawdown': f"{metrics.get('risk', {}).get('max_drawdown', 0):.2f}%"
        }
    
    def save_report(self, filename: str = 'trading_report.json'):
        """Save report to file"""
        report = self.generate_full_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"Report saved to {filename}")
    
    def print_report(self):
        """Print formatted report to console"""
        report = self.generate_full_report()
        
        print("\n" + "="*60)
        print("TRADING STRATEGY PERFORMANCE REPORT")
        print("="*60)
        
        print(f"\nGenerated: {report['generated_at']}")
        print(f"Strategy: {self.config.get('strategy_name', 'Unknown')}")
        
        print("\n📊 EXECUTIVE SUMMARY")
        print("-"*40)
        for key, value in report['summary'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n🤖 AI INSIGHTS")
        print("-"*40)
        print(report['ai_insights'])
        
        print("\n💡 RECOMMENDATIONS")
        print("-"*40)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*60)