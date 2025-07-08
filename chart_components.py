"""
Interactive chart components for Scalparo Trading Backtester
Enhanced with TradingView-style modern interface and technical indicators
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class TechnicalIndicators:
    """Calculate technical indicators for chart display"""
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict:
        """Calculate Bollinger Bands"""
        sma = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        
        return {
            'middle': sma,
            'upper': sma + (std * std_dev),
            'lower': sma - (std * std_dev)
        }


class ChartGenerator:
    """Generates interactive charts for trading analysis with TradingView-style interface"""
    
    def __init__(self):
        self.colors = {
            'bullish': '#26A69A',
            'bearish': '#EF5350',
            'buy_signal': '#4CAF50',
            'sell_signal': '#F44336',
            'volume': '#42A5F5',
            'strategy': '#9C27B0',
            'benchmark': '#FF9800',
            'ema_fast': '#2196F3',
            'ema_slow': '#FF5722',
            'rsi': '#9C27B0',
            'macd': '#607D8B',
            'signal': '#FF9800',
            'bb_upper': '#E91E63',
            'bb_lower': '#E91E63',
            'bb_middle': '#9E9E9E'
        }
        
        self.chart_theme = {
            'bgcolor': '#1E1E1E',
            'paper_bgcolor': '#1E1E1E',
            'plot_bgcolor': '#1E1E1E',
            'gridcolor': '#2D2D2D',
            'font_color': '#FFFFFF'
        }
    
    def create_advanced_trading_chart(self, data: pd.DataFrame, signals: Optional[Dict] = None, 
                                     indicators: Optional[Dict] = None, chart_type: str = 'candlestick',
                                     show_volume: bool = True, show_indicators: bool = True,
                                     strategy_data: Optional[Dict] = None) -> go.Figure:
        """Create advanced TradingView-style trading chart with multiple panels"""
        
        # Determine number of subplots based on indicators
        rows = 1
        row_heights = [0.7]
        subplot_titles = ['Price Chart']
        
        if show_volume:
            rows += 1
            row_heights.append(0.15)
            subplot_titles.append('Volume')
        
        if show_indicators and indicators:
            if 'rsi' in indicators:
                rows += 1
                row_heights.append(0.15)
                subplot_titles.append('RSI')
            if 'macd' in indicators:
                rows += 1
                row_heights.append(0.15)
                subplot_titles.append('MACD')
        
        # Normalize row heights
        if len(row_heights) > 1:
            row_heights[0] = 0.5  # Main chart gets 50%
            remaining = 0.5 / (len(row_heights) - 1)
            for i in range(1, len(row_heights)):
                row_heights[i] = remaining
        
        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=subplot_titles,
            row_heights=row_heights,
            specs=[[{"secondary_y": True}] if i == 0 else [{}] for i in range(rows)]
        )
        
        current_row = 1
        
        # Add main price chart (candlestick or line)
        if chart_type == 'candlestick':
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='OHLC',
                    increasing_line_color=self.colors['bullish'],
                    decreasing_line_color=self.colors['bearish'],
                    increasing_fillcolor=self.colors['bullish'],
                    decreasing_fillcolor=self.colors['bearish']
                ),
                row=current_row, col=1
            )
        else:  # line chart
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color=self.colors['strategy'], width=2)
                ),
                row=current_row, col=1
            )
        
        # Add technical indicators to main chart if enabled
        if show_indicators and indicators:
            # Bollinger Bands
            if 'bollinger' in indicators:
                bb = indicators['bollinger']
                fig.add_trace(
                    go.Scatter(
                        x=data.index, y=bb['upper'], 
                        mode='lines', name='BB Upper',
                        line=dict(color=self.colors['bb_upper'], width=1, dash='dot'),
                        showlegend=False
                    ), row=current_row, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=data.index, y=bb['lower'],
                        mode='lines', name='BB Lower',
                        line=dict(color=self.colors['bb_lower'], width=1, dash='dot'),
                        fill='tonexty', fillcolor='rgba(233, 30, 99, 0.1)',
                        showlegend=False
                    ), row=current_row, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=data.index, y=bb['middle'],
                        mode='lines', name='BB Middle',
                        line=dict(color=self.colors['bb_middle'], width=1)
                    ), row=current_row, col=1
                )
            
            # EMAs
            if 'ema_12' in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=data.index, y=indicators['ema_12'],
                        mode='lines', name='EMA 12',
                        line=dict(color=self.colors['ema_fast'], width=2)
                    ), row=current_row, col=1
                )
            
            if 'ema_26' in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=data.index, y=indicators['ema_26'],
                        mode='lines', name='EMA 26',
                        line=dict(color=self.colors['ema_slow'], width=2)
                    ), row=current_row, col=1
                )
        
        # Add strategy prediction line if provided
        if strategy_data and 'predictions' in strategy_data:
            fig.add_trace(
                go.Scatter(
                    x=strategy_data['predictions'].index,
                    y=strategy_data['predictions'].values,
                    mode='lines',
                    name='Strategy Prediction',
                    line=dict(color=self.colors['strategy'], width=3, dash='dash'),
                    opacity=0.8
                ), row=current_row, col=1
            )
        
        # Add buy/sell signals
        if signals:
            if 'buy_signals' in signals and len(signals['buy_signals']) > 0:
                buy_signals = signals['buy_signals']
                fig.add_trace(
                    go.Scatter(
                        x=buy_signals['timestamp'],
                        y=buy_signals['price'],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-up',
                            size=15,
                            color=self.colors['buy_signal'],
                            line=dict(width=2, color='white')
                        ),
                        name='Buy Signal',
                        hovertemplate='<b>Buy Signal</b><br>Time: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                    ), row=current_row, col=1
                )
            
            if 'sell_signals' in signals and len(signals['sell_signals']) > 0:
                sell_signals = signals['sell_signals']
                fig.add_trace(
                    go.Scatter(
                        x=sell_signals['timestamp'],
                        y=sell_signals['price'],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-down',
                            size=15,
                            color=self.colors['sell_signal'],
                            line=dict(width=2, color='white')
                        ),
                        name='Sell Signal',
                        hovertemplate='<b>Sell Signal</b><br>Time: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                    ), row=current_row, col=1
                )
        
        current_row += 1
        
        # Add volume chart if enabled
        if show_volume:
            volume_colors = ['red' if close < open else 'green' 
                           for close, open in zip(data['Close'], data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color=volume_colors,
                    opacity=0.7,
                    showlegend=False
                ), row=current_row, col=1
            )
            current_row += 1
        
        # Add RSI if enabled
        if show_indicators and indicators and 'rsi' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=indicators['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.colors['rsi'], width=2),
                    showlegend=False
                ), row=current_row, col=1
            )
            
            # Add RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=current_row, col=1)
            
            # Update RSI y-axis
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
            current_row += 1
        
        # Add MACD if enabled
        if show_indicators and indicators and 'macd' in indicators:
            macd_data = indicators['macd']
            
            # MACD line
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=macd_data['macd'],
                    mode='lines',
                    name='MACD',
                    line=dict(color=self.colors['macd'], width=2),
                    showlegend=False
                ), row=current_row, col=1
            )
            
            # Signal line
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=macd_data['signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color=self.colors['signal'], width=2),
                    showlegend=False
                ), row=current_row, col=1
            )
            
            # Histogram
            histogram_colors = ['green' if h > 0 else 'red' for h in macd_data['histogram']]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=macd_data['histogram'],
                    name='MACD Histogram',
                    marker_color=histogram_colors,
                    opacity=0.6,
                    showlegend=False
                ), row=current_row, col=1
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=current_row, col=1)
            fig.update_yaxes(title_text="MACD", row=current_row, col=1)
        
        # Apply TradingView-style theme
        fig.update_layout(
            title={
                'text': 'Advanced Trading Chart',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': self.chart_theme['font_color']}
            },
            paper_bgcolor=self.chart_theme['paper_bgcolor'],
            plot_bgcolor=self.chart_theme['plot_bgcolor'],
            font_color=self.chart_theme['font_color'],
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update all axes styling
        for i in range(1, rows + 1):
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=self.chart_theme['gridcolor'],
                showspikes=True,
                spikecolor="white",
                spikesnap="cursor",
                spikemode="across",
                row=i, col=1
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=self.chart_theme['gridcolor'],
                showspikes=True,
                spikecolor="white",
                spikesnap="cursor",
                spikemode="across",
                row=i, col=1
            )
        
        # Only show x-axis title on bottom chart
        fig.update_xaxes(title_text="Time", row=rows, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        
        return fig
    
    def create_candlestick_chart(self, data: pd.DataFrame, signals: Optional[Dict] = None, 
                               indicators: Optional[Dict] = None) -> go.Figure:
        """Legacy method - now calls advanced trading chart"""
        return self.create_advanced_trading_chart(
            data=data, 
            signals=signals, 
            indicators=indicators,
            chart_type='candlestick',
            show_volume=True,
            show_indicators=True
        )
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate all available technical indicators"""
        indicators = {}
        
        # EMAs
        indicators['ema_12'] = TechnicalIndicators.ema(data['Close'], 12)
        indicators['ema_26'] = TechnicalIndicators.ema(data['Close'], 26)
        
        # RSI
        indicators['rsi'] = TechnicalIndicators.rsi(data['Close'])
        
        # MACD
        indicators['macd'] = TechnicalIndicators.macd(data['Close'])
        
        # Bollinger Bands
        indicators['bollinger'] = TechnicalIndicators.bollinger_bands(data['Close'])
        
        return indicators
    
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
    
    def create_enhanced_price_histogram(self, data: pd.DataFrame, strategy_signals: Optional[Dict] = None,
                                      buy_hold_signals: Optional[Dict] = None, bins: int = 50) -> go.Figure:
        """Create enhanced price histogram with buy/hold/strategy indication overlays for testing"""
        
        # Create subplots: histogram and time series
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.1,
            subplot_titles=('Price Distribution vs Time', 'Strategy Performance Comparison'),
            row_heights=[0.6, 0.4],
            specs=[[{"secondary_y": True}], [{}]]
        )
        
        # Create 2D histogram (price vs time)
        # Convert datetime index to numeric for histogram
        time_numeric = pd.to_numeric(data.index)
        
        fig.add_trace(
            go.Histogram2d(
                x=time_numeric,
                y=data['Close'],
                nbinsx=30,
                nbinsy=bins,
                colorscale='Viridis',
                name='Price-Time Distribution',
                hovertemplate='<b>Price-Time Distribution</b><br>' +
                            'Time: %{x}<br>' +
                            'Price: $%{y:.2f}<br>' +
                            'Frequency: %{z}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add strategy signals overlay on time axis
        if strategy_signals:
            if 'buy_signals' in strategy_signals:
                buy_signals = strategy_signals['buy_signals']
                if len(buy_signals) > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=pd.to_numeric(buy_signals['timestamp']),
                            y=buy_signals['price'],
                            mode='markers',
                            marker=dict(
                                symbol='triangle-up',
                                size=12,
                                color=self.colors['buy_signal'],
                                line=dict(width=2, color='white')
                            ),
                            name='Strategy Buy',
                            hovertemplate='<b>Strategy Buy</b><br>Time: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                        ),
                        row=1, col=1
                    )
            
            if 'sell_signals' in strategy_signals:
                sell_signals = strategy_signals['sell_signals']
                if len(sell_signals) > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=pd.to_numeric(sell_signals['timestamp']),
                            y=sell_signals['price'],
                            mode='markers',
                            marker=dict(
                                symbol='triangle-down',
                                size=12,
                                color=self.colors['sell_signal'],
                                line=dict(width=2, color='white')
                            ),
                            name='Strategy Sell',
                            hovertemplate='<b>Strategy Sell</b><br>Time: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                        ),
                        row=1, col=1
                    )
        
        # Add buy & hold indicators if provided
        if buy_hold_signals:
            if 'buy_signals' in buy_hold_signals:
                bh_buy = buy_hold_signals['buy_signals']
                if len(bh_buy) > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=pd.to_numeric(bh_buy['timestamp']),
                            y=bh_buy['price'],
                            mode='markers',
                            marker=dict(
                                symbol='circle',
                                size=10,
                                color=self.colors['benchmark'],
                                line=dict(width=2, color='white')
                            ),
                            name='Buy & Hold Entry',
                            hovertemplate='<b>Buy & Hold Entry</b><br>Time: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                        ),
                        row=1, col=1
                    )
        
        # Add price line overlay
        fig.add_trace(
            go.Scatter(
                x=time_numeric,
                y=data['Close'],
                mode='lines',
                name='Price Line',
                line=dict(color='white', width=2, dash='dash'),
                opacity=0.8,
                yaxis='y2'
            ),
            row=1, col=1, secondary_y=True
        )
        
        # Bottom chart: Performance comparison bars
        if strategy_signals and buy_hold_signals:
            # Calculate simple performance metrics for visualization
            strategy_trades = len(strategy_signals.get('buy_signals', [])) + len(strategy_signals.get('sell_signals', []))
            buy_hold_trades = len(buy_hold_signals.get('buy_signals', []))
            
            # Sample performance data (replace with actual calculations)
            performance_data = {
                'Strategy': [strategy_trades, 15.2, 8.5],  # Trades, Return%, Volatility%
                'Buy & Hold': [buy_hold_trades, 12.8, 12.1]
            }
            
            metrics = ['Trades', 'Return (%)', 'Volatility (%)']
            
            fig.add_trace(
                go.Bar(
                    x=metrics,
                    y=performance_data['Strategy'],
                    name='Strategy Performance',
                    marker_color=self.colors['strategy'],
                    opacity=0.8,
                    hovertemplate='<b>Strategy</b><br>%{x}: %{y}<extra></extra>'
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=metrics,
                    y=performance_data['Buy & Hold'],
                    name='Buy & Hold Performance',
                    marker_color=self.colors['benchmark'],
                    opacity=0.8,
                    hovertemplate='<b>Buy & Hold</b><br>%{x}: %{y}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Apply styling
        fig.update_layout(
            title={
                'text': 'Enhanced Price Distribution & Strategy Analysis',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=700,
            showlegend=True,
            hovermode='closest',
            paper_bgcolor=self.chart_theme['paper_bgcolor'],
            plot_bgcolor=self.chart_theme['plot_bgcolor'],
            font_color=self.chart_theme['font_color']
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1, secondary_y=True)
        
        fig.update_xaxes(title_text="Metrics", row=2, col=1)
        fig.update_yaxes(title_text="Value", row=2, col=1)
        
        return fig
    
    def create_strategy_indicator_chart(self, data: pd.DataFrame, strategy_name: str, 
                                      strategy_indicators: Dict) -> go.Figure:
        """Create chart showing indicators used by specific strategy"""
        
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color=self.colors['strategy'], width=2),
                yaxis='y2'
            )
        )
        
        # Add strategy-specific indicators
        for indicator_name, indicator_data in strategy_indicators.items():
            if indicator_name == 'ema':
                for period, values in indicator_data.items():
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=values,
                            mode='lines',
                            name=f'EMA {period}',
                            line=dict(width=2),
                            yaxis='y2'
                        )
                    )
            elif indicator_name == 'rsi':
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicator_data,
                        mode='lines',
                        name='RSI',
                        line=dict(color=self.colors['rsi'], width=2),
                        yaxis='y'
                    )
                )
            elif indicator_name == 'macd':
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicator_data['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color=self.colors['macd'], width=2),
                        yaxis='y'
                    )
                )
        
        # Create secondary y-axis layout
        fig.update_layout(
            title=f'{strategy_name} - Strategy Indicators',
            xaxis_title='Time',
            yaxis=dict(
                title='Indicator Values',
                side='left'
            ),
            yaxis2=dict(
                title='Price ($)',
                side='right',
                overlaying='y'
            ),
            height=500,
            hovermode='x unified',
            paper_bgcolor=self.chart_theme['paper_bgcolor'],
            plot_bgcolor=self.chart_theme['plot_bgcolor'],
            font_color=self.chart_theme['font_color']
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