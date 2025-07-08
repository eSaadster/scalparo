"""
Interactive chart components for Scalparo Trading Backtester
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class ChartGenerator:
    """Generates interactive charts for trading analysis"""
    
    def __init__(self):
        # Updated color palette for better visual fidelity
        self.colors = {
            'bullish': '#26a69a',
            'bearish': '#ef5350',
            'buy_signal': '#2ecc71',
            'sell_signal': '#e74c3c',
            'volume': '#338cf5',
            'strategy': '#2196F3',
            'benchmark': '#FF9800'
        }
    
    def create_candlestick_chart(
        self,
        data: pd.DataFrame,
        signals: Optional[Dict] = None,
        indicators: Optional[Dict[str, pd.Series]] = None
    ) -> go.Figure:
        """Create interactive candlestick chart with advanced features"""

        indicator_names = list(indicators.keys()) if indicators else []
        indicator_count = len(indicator_names)

        # Build subplots: price, indicator panels, volume
        rows = 2 + indicator_count
        row_heights = [0.55] + [0.15] * indicator_count + [0.3]
        titles = ['Price'] + indicator_names + ['Volume']

        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=tuple(titles),
            row_heights=row_heights
        )
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color=self.colors['bullish'],
                decreasing_line_color=self.colors['bearish'],
                showlegend=False,
            ),
            row=1, col=1
        )
        
        # Add volume bars
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=self.colors['volume'],
                opacity=0.6,
                showlegend=False,
            ),
            row=rows, col=1
        )
        
        # Add buy/sell signals if provided
        if signals:
            if 'buy_signals' in signals:
                buy_signals = signals['buy_signals']
                fig.add_trace(
                    go.Scatter(
                        x=buy_signals['timestamp'],
                        y=buy_signals['price'],
                        mode='markers+text',
                        marker=dict(
                            symbol='triangle-up',
                            size=12,
                            color=self.colors['buy_signal'],
                            line=dict(width=1, color='black'),
                        ),
                        text=[f"BUY\n${p:.2f}" for p in buy_signals['price']],
                        textposition='bottom center',
                        name='Buy Signal',
                        hovertemplate='<b>Buy</b><br>Time: %{x}<br>Price: $%{y:.2f}<extra></extra>',
                        showlegend=False,
                    ),
                    row=1, col=1
                )

            if 'sell_signals' in signals:
                sell_signals = signals['sell_signals']
                fig.add_trace(
                    go.Scatter(
                        x=sell_signals['timestamp'],
                        y=sell_signals['price'],
                        mode='markers+text',
                        marker=dict(
                            symbol='triangle-down',
                            size=12,
                            color=self.colors['sell_signal'],
                            line=dict(width=1, color='black'),
                        ),
                        text=[f"SELL\n${p:.2f}" for p in sell_signals['price']],
                        textposition='top center',
                        name='Sell Signal',
                        hovertemplate='<b>Sell</b><br>Time: %{x}<br>Price: $%{y:.2f}<extra></extra>',
                        showlegend=False,
                    ),
                    row=1, col=1
                )
        
        # Add technical indicators if provided
        if indicators:
            for i, (indicator_name, indicator_data) in enumerate(indicators.items(), start=2):
                fig.add_trace(
                    go.Scatter(
                        x=indicator_data.index,
                        y=indicator_data.values,
                        mode='lines',
                        name=indicator_name,
                        line=dict(width=1.5),
                        opacity=0.8,
                        showlegend=False,
                    ),
                    row=i, col=1
                )

                # Annotate last value
                fig.add_annotation(
                    x=indicator_data.index[-1],
                    y=indicator_data.values[-1],
                    text=f"{indicator_data.values[-1]:.2f}",
                    showarrow=False,
                    xref=f"x{i}",
                    yref=f"y{i}",
                    xanchor="left",
                )

                # Threshold lines for RSI
                if indicator_name.upper() == 'RSI':
                    fig.add_hline(y=70, line_dash='dash', line_color='orange', row=i, col=1)
                    fig.add_hline(y=30, line_dash='dash', line_color='orange', row=i, col=1)
        
        # Determine last price information for header
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
        change = last_close - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0
        price_color = self.colors['bullish'] if change >= 0 else self.colors['bearish']

        header_html = (
            f"<span style='color:{price_color};font-size:20px;'>$"
            f"{last_close:.2f} ({change:+.2f} / {change_pct:+.2f}%)</span>"
            f"<span style='margin-left:20px;font-size:12px;'>"
            f"O:{data['Open'].iloc[-1]:.2f} H:{data['High'].iloc[-1]:.2f} "
            f"L:{data['Low'].iloc[-1]:.2f} V:{data['Volume'].iloc[-1]:,.0f}""</span>"
        )

        fig.update_layout(
            title=header_html,
            xaxis_rangeslider_visible=False,
            height=700,
            hovermode='x unified',
            template='plotly_white',
            dragmode='pan',
        )

        fig.update_xaxes(
            title_text="Time",
            showgrid=True,
            gridcolor="#E1E4E8",
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikecolor="grey",
            spikethickness=1,
        )

        fig.update_yaxes(showgrid=True, gridcolor="#E1E4E8")

        # Set axis titles for main panels
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=rows, col=1)

        # Add time range selector buttons
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label='1D', step='day', stepmode='backward'),
                        dict(count=5, label='5D', step='day', stepmode='backward'),
                        dict(count=1, label='1M', step='month', stepmode='backward'),
                        dict(count=3, label='3M', step='month', stepmode='backward'),
                        dict(count=6, label='6M', step='month', stepmode='backward'),
                        dict(step='all', label='All')
                    ]
                ),
                rangeslider=dict(visible=False)
            )
        )
        
        return fig
    
    def create_performance_comparison(self, strategy_returns: pd.Series, 
                                    benchmark_returns: pd.Series) -> go.Figure:
        """Create strategy vs benchmark comparison chart"""
        
        # Calculate cumulative returns
        strategy_cumulative = (1 + strategy_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        fig = go.Figure()
        
        # Add strategy performance
        fig.add_trace(
            go.Scatter(
                x=strategy_cumulative.index,
                y=strategy_cumulative.values,
                mode='lines',
                name='Strategy',
                line=dict(color=self.colors['strategy'], width=2),
                hovertemplate='<b>Strategy</b><br>' +
                            'Date: %{x}<br>' +
                            'Cumulative Return: %{y:.3f}<extra></extra>'
            )
        )
        
        # Add benchmark performance
        fig.add_trace(
            go.Scatter(
                x=benchmark_cumulative.index,
                y=benchmark_cumulative.values,
                mode='lines',
                name='Buy & Hold',
                line=dict(color=self.colors['benchmark'], width=2),
                hovertemplate='<b>Buy & Hold</b><br>' +
                            'Date: %{x}<br>' +
                            'Cumulative Return: %{y:.3f}<extra></extra>'
            )
        )
        
        # Add divergence fill
        fig.add_trace(
            go.Scatter(
                x=strategy_cumulative.index,
                y=strategy_cumulative.values,
                fill='tonexty',
                mode='none',
                fillcolor='rgba(33, 150, 243, 0.1)',
                name='Performance Divergence',
                showlegend=False
            )
        )
        
        fig.update_layout(
            title='Strategy vs Buy & Hold Performance',
            xaxis_title='Date',
            yaxis_title='Cumulative Return',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_price_histogram(self, data: pd.DataFrame, bins: int = 50) -> go.Figure:
        """Create price distribution histogram"""
        
        fig = go.Figure()
        
        # Add histogram
        fig.add_trace(
            go.Histogram(
                x=data['Close'],
                nbinsx=bins,
                name='Price Distribution',
                marker_color=self.colors['strategy'],
                opacity=0.7,
                hovertemplate='<b>Price Range</b><br>' +
                            'Price: $%{x:.2f}<br>' +
                            'Frequency: %{y}<extra></extra>'
            )
        )
        
        # Add mean line
        mean_price = data['Close'].mean()
        fig.add_vline(
            x=mean_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: ${mean_price:.2f}",
            annotation_position="top right"
        )
        
        # Add median line
        median_price = data['Close'].median()
        fig.add_vline(
            x=median_price,
            line_dash="dot",
            line_color="orange",
            annotation_text=f"Median: ${median_price:.2f}",
            annotation_position="top left"
        )
        
        fig.update_layout(
            title='Price Distribution Analysis',
            xaxis_title='Price ($)',
            yaxis_title='Frequency',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_drawdown_chart(self, returns: pd.Series) -> go.Figure:
        """Create underwater equity curve showing drawdown periods"""
        
        # Calculate cumulative returns and running maximum
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        fig = go.Figure()
        
        # Add drawdown area
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown.values * 100,  # Convert to percentage
                fill='tozeroy',
                mode='lines',
                name='Drawdown',
                line=dict(color=self.colors['bearish']),
                fillcolor='rgba(255, 68, 68, 0.3)',
                hovertemplate='<b>Drawdown</b><br>' +
                            'Date: %{x}<br>' +
                            'Drawdown: %{y:.2f}%<extra></extra>'
            )
        )
        
        # Add zero line
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            opacity=0.5
        )
        
        fig.update_layout(
            title='Underwater Equity Curve',
            xaxis_title='Date',
            yaxis_title='Drawdown (%)',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_trade_timeline(self, trades: List[Dict]) -> go.Figure:
        """Create chronological view of all trades with P&L"""
        
        if not trades:
            # Return empty chart if no trades
            fig = go.Figure()
            fig.update_layout(
                title='Trade Timeline',
                xaxis_title='Trade Number',
                yaxis_title='P&L ($)',
                height=400,
                annotations=[dict(
                    text="No trades to display",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font_size=16
                )]
            )
            return fig
        
        # Prepare trade data
        trade_numbers = list(range(1, len(trades) + 1))
        pnl_values = [trade.get('pnl', 0) for trade in trades]
        trade_types = ['Win' if pnl > 0 else 'Loss' for pnl in pnl_values]
        
        # Create scatter plot
        fig = go.Figure()
        
        # Add winning trades
        winning_trades = [(i, pnl) for i, pnl in zip(trade_numbers, pnl_values) if pnl > 0]
        if winning_trades:
            win_numbers, win_pnl = zip(*winning_trades)
            fig.add_trace(
                go.Scatter(
                    x=win_numbers,
                    y=win_pnl,
                    mode='markers',
                    marker=dict(
                        color=self.colors['bullish'],
                        size=8,
                        symbol='circle'
                    ),
                    name='Winning Trades',
                    hovertemplate='<b>Trade #%{x}</b><br>' +
                                'P&L: $%{y:.2f}<br>' +
                                'Result: Win<extra></extra>'
                )
            )
        
        # Add losing trades
        losing_trades = [(i, pnl) for i, pnl in zip(trade_numbers, pnl_values) if pnl <= 0]
        if losing_trades:
            loss_numbers, loss_pnl = zip(*losing_trades)
            fig.add_trace(
                go.Scatter(
                    x=loss_numbers,
                    y=loss_pnl,
                    mode='markers',
                    marker=dict(
                        color=self.colors['bearish'],
                        size=8,
                        symbol='circle'
                    ),
                    name='Losing Trades',
                    hovertemplate='<b>Trade #%{x}</b><br>' +
                                'P&L: $%{y:.2f}<br>' +
                                'Result: Loss<extra></extra>'
                )
            )
        
        # Add zero line
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            opacity=0.5
        )
        
        fig.update_layout(
            title='Trade Timeline & P&L Distribution',
            xaxis_title='Trade Number',
            yaxis_title='P&L ($)',
            height=400,
            hovermode='closest'
        )
        
        return fig
    
    def create_rolling_metrics_chart(self, returns: pd.Series, window: int = 30) -> go.Figure:
        """Create rolling performance metrics chart"""
        
        # Calculate rolling metrics
        rolling_returns = returns.rolling(window=window).mean() * 252  # Annualized
        rolling_volatility = returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
        rolling_sharpe = rolling_returns / rolling_volatility
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f'Rolling Returns ({window}-day)',
                f'Rolling Volatility ({window}-day)', 
                f'Rolling Sharpe Ratio ({window}-day)'
            )
        )
        
        # Add rolling returns
        fig.add_trace(
            go.Scatter(
                x=rolling_returns.index,
                y=rolling_returns.values * 100,
                mode='lines',
                name='Rolling Returns',
                line=dict(color=self.colors['strategy']),
                hovertemplate='Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add rolling volatility
        fig.add_trace(
            go.Scatter(
                x=rolling_volatility.index,
                y=rolling_volatility.values * 100,
                mode='lines',
                name='Rolling Volatility',
                line=dict(color=self.colors['bearish']),
                hovertemplate='Date: %{x}<br>Volatility: %{y:.2f}%<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Add rolling Sharpe ratio
        fig.add_trace(
            go.Scatter(
                x=rolling_sharpe.index,
                y=rolling_sharpe.values,
                mode='lines',
                name='Rolling Sharpe',
                line=dict(color=self.colors['bullish']),
                hovertemplate='Date: %{x}<br>Sharpe: %{y:.2f}<extra></extra>'
            ),
            row=3, col=1
        )
        
        # Add Sharpe reference line at 1.0
        fig.add_hline(
            y=1.0,
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            row=3, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title=f'Rolling Performance Metrics ({window}-day window)'
        )
        
        # Update axes
        fig.update_yaxes(title_text="Return (%)", row=1, col=1)
        fig.update_yaxes(title_text="Volatility (%)", row=2, col=1)
        fig.update_yaxes(title_text="Sharpe Ratio", row=3, col=1)
        fig.update_xaxes(title_text="Date", row=3, col=1)
        
        return fig
    
    def create_risk_return_scatter(self, strategy_data: Dict, benchmark_data: Dict) -> go.Figure:
        """Create risk vs return scatter plot"""
        
        fig = go.Figure()
        
        # Add strategy point
        fig.add_trace(
            go.Scatter(
                x=[strategy_data['volatility']],
                y=[strategy_data['return']],
                mode='markers',
                marker=dict(
                    color=self.colors['strategy'],
                    size=15,
                    symbol='circle'
                ),
                name='Strategy',
                hovertemplate='<b>Strategy</b><br>' +
                            'Risk (Volatility): %{x:.2f}%<br>' +
                            'Return: %{y:.2f}%<br>' +
                            'Sharpe: ' + f"{strategy_data.get('sharpe', 0):.2f}" + '<extra></extra>'
            )
        )
        
        # Add benchmark point
        fig.add_trace(
            go.Scatter(
                x=[benchmark_data['volatility']],
                y=[benchmark_data['return']],
                mode='markers',
                marker=dict(
                    color=self.colors['benchmark'],
                    size=15,
                    symbol='square'
                ),
                name='Buy & Hold',
                hovertemplate='<b>Buy & Hold</b><br>' +
                            'Risk (Volatility): %{x:.2f}%<br>' +
                            'Return: %{y:.2f}%<br>' +
                            'Sharpe: ' + f"{benchmark_data.get('sharpe', 0):.2f}" + '<extra></extra>'
            )
        )
        
        # Add efficient frontier reference (simplified)
        risk_range = np.linspace(0, max(strategy_data['volatility'], benchmark_data['volatility']) * 1.2, 100)
        sharpe_1_line = risk_range * 1.0  # Sharpe ratio = 1 line
        
        fig.add_trace(
            go.Scatter(
                x=risk_range,
                y=sharpe_1_line,
                mode='lines',
                line=dict(dash='dot', color='gray'),
                name='Sharpe = 1.0',
                hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
            )
        )
        
        fig.update_layout(
            title='Risk-Return Analysis',
            xaxis_title='Risk (Volatility %)',
            yaxis_title='Return (%)',
            height=500,
            hovermode='closest'
        )
        
        return fig