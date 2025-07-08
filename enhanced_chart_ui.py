"""
Enhanced Chart UI Components for TradingView-style interface
"""
import streamlit as st
import pandas as pd
from typing import Dict, Optional, List
from chart_components import ChartGenerator, TechnicalIndicators


class EnhancedChartUI:
    """Enhanced UI components for TradingView-style charts"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
    
    def render_chart_controls(self) -> Dict:
        """Render chart control panel and return settings"""
        
        st.markdown("### 📊 Chart Settings")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            chart_type = st.selectbox(
                "Chart Type",
                ["candlestick", "line"],
                index=0,
                help="Select between candlestick and line chart"
            )
        
        with col2:
            show_volume = st.checkbox(
                "Show Volume",
                value=True,
                help="Display volume bars below price chart"
            )
        
        with col3:
            show_indicators = st.checkbox(
                "Show Indicators",
                value=True,
                help="Display technical indicators"
            )
        
        with col4:
            dark_theme = st.checkbox(
                "Dark Theme",
                value=True,
                help="Use dark TradingView-style theme"
            )
        
        return {
            'chart_type': chart_type,
            'show_volume': show_volume,
            'show_indicators': show_indicators,
            'dark_theme': dark_theme
        }
    
    def render_indicator_controls(self) -> Dict:
        """Render indicator selection controls"""
        
        st.markdown("### 🔧 Technical Indicators")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trend Indicators**")
            show_ema = st.checkbox("EMA (12, 26)", value=True)
            show_bollinger = st.checkbox("Bollinger Bands", value=False)
        
        with col2:
            st.markdown("**Momentum Indicators**")
            show_rsi = st.checkbox("RSI (14)", value=True)
            show_macd = st.checkbox("MACD", value=True)
        
        return {
            'show_ema': show_ema,
            'show_bollinger': show_bollinger,
            'show_rsi': show_rsi,
            'show_macd': show_macd
        }
    
    def render_strategy_controls(self, available_strategies: List[str]) -> Dict:
        """Render strategy-specific controls"""
        
        st.markdown("### 🎯 Strategy Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_strategy = st.selectbox(
                "Strategy",
                available_strategies,
                help="Select strategy to analyze"
            )
        
        with col2:
            show_predictions = st.checkbox(
                "Show Predictions",
                value=True,
                help="Display strategy prediction overlay"
            )
        
        # Strategy-specific indicator information
        if selected_strategy:
            st.info(f"📋 **{selected_strategy}** uses: EMA, MACD, RSI indicators")
        
        return {
            'selected_strategy': selected_strategy,
            'show_predictions': show_predictions
        }
    
    def render_advanced_chart(self, data: pd.DataFrame, signals: Optional[Dict] = None,
                            chart_settings: Optional[Dict] = None,
                            indicator_settings: Optional[Dict] = None,
                            strategy_data: Optional[Dict] = None) -> None:
        """Render the advanced TradingView-style chart"""
        
        # Use default settings if not provided
        if chart_settings is None:
            chart_settings = {
                'chart_type': 'candlestick',
                'show_volume': True,
                'show_indicators': True,
                'dark_theme': True
            }
        
        if indicator_settings is None:
            indicator_settings = {
                'show_ema': True,
                'show_bollinger': False,
                'show_rsi': True,
                'show_macd': True
            }
        
        # Calculate indicators based on settings
        indicators = {}
        if chart_settings['show_indicators']:
            if indicator_settings['show_ema']:
                indicators['ema_12'] = TechnicalIndicators.ema(data['Close'], 12)
                indicators['ema_26'] = TechnicalIndicators.ema(data['Close'], 26)
            
            if indicator_settings['show_bollinger']:
                indicators['bollinger'] = TechnicalIndicators.bollinger_bands(data['Close'])
            
            if indicator_settings['show_rsi']:
                indicators['rsi'] = TechnicalIndicators.rsi(data['Close'])
            
            if indicator_settings['show_macd']:
                indicators['macd'] = TechnicalIndicators.macd(data['Close'])
        
        # Create the chart
        fig = self.chart_generator.create_advanced_trading_chart(
            data=data,
            signals=signals,
            indicators=indicators if indicators else None,
            chart_type=chart_settings['chart_type'],
            show_volume=chart_settings['show_volume'],
            show_indicators=chart_settings['show_indicators'],
            strategy_data=strategy_data
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, height=800)
        
        # Add chart statistics
        self._render_chart_stats(data, signals)
    
    def render_testing_histogram(self, data: pd.DataFrame, 
                                strategy_signals: Optional[Dict] = None,
                                buy_hold_signals: Optional[Dict] = None) -> None:
        """Render enhanced price histogram for testing section"""
        
        st.markdown("### 📈 Price Distribution & Strategy Analysis")
        
        fig = self.chart_generator.create_enhanced_price_histogram(
            data=data,
            strategy_signals=strategy_signals,
            buy_hold_signals=buy_hold_signals
        )
        
        st.plotly_chart(fig, use_container_width=True, height=700)
    
    def render_strategy_indicator_analysis(self, data: pd.DataFrame, 
                                         strategy_name: str) -> None:
        """Render strategy-specific indicator analysis"""
        
        st.markdown(f"### 🎯 {strategy_name} - Indicator Analysis")
        
        # Calculate strategy-specific indicators (this would be dynamic based on strategy)
        strategy_indicators = {
            'ema': {
                12: TechnicalIndicators.ema(data['Close'], 12),
                26: TechnicalIndicators.ema(data['Close'], 26)
            },
            'rsi': TechnicalIndicators.rsi(data['Close']),
            'macd': TechnicalIndicators.macd(data['Close'])
        }
        
        fig = self.chart_generator.create_strategy_indicator_chart(
            data=data,
            strategy_name=strategy_name,
            strategy_indicators=strategy_indicators
        )
        
        st.plotly_chart(fig, use_container_width=True, height=500)
        
        # Add strategy insights
        self._render_strategy_insights(strategy_name, strategy_indicators)
    
    def _render_chart_stats(self, data: pd.DataFrame, signals: Optional[Dict] = None) -> None:
        """Render chart statistics panel"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                f"${data['Close'].iloc[-1]:.2f}",
                delta=f"{((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100:.2f}%"
            )
        
        with col2:
            volume_avg = data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            volume_change = ((current_volume / volume_avg) - 1) * 100
            st.metric(
                "Volume vs Avg",
                f"{current_volume:,.0f}",
                delta=f"{volume_change:.1f}%"
            )
        
        with col3:
            if signals and 'buy_signals' in signals:
                buy_count = len(signals['buy_signals'])
                st.metric("Buy Signals", buy_count)
            else:
                st.metric("Buy Signals", 0)
        
        with col4:
            if signals and 'sell_signals' in signals:
                sell_count = len(signals['sell_signals'])
                st.metric("Sell Signals", sell_count)
            else:
                st.metric("Sell Signals", 0)
    
    def _render_strategy_insights(self, strategy_name: str, indicators: Dict) -> None:
        """Render strategy-specific insights"""
        
        st.markdown("#### 💡 Strategy Insights")
        
        # Calculate current indicator values
        current_rsi = indicators['rsi'].iloc[-1] if 'rsi' in indicators else None
        current_macd = indicators['macd']['macd'].iloc[-1] if 'macd' in indicators else None
        
        col1, col2 = st.columns(2)
        
        with col1:
            if current_rsi is not None:
                rsi_signal = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
                st.info(f"**RSI**: {current_rsi:.1f} ({rsi_signal})")
        
        with col2:
            if current_macd is not None:
                macd_signal = "Bullish" if current_macd > 0 else "Bearish"
                st.info(f"**MACD**: {current_macd:.3f} ({macd_signal})")
    
    def render_timeframe_selector(self) -> str:
        """Render timeframe selection for charts"""
        
        timeframes = {
            "1m": "1 Minute",
            "5m": "5 Minutes", 
            "15m": "15 Minutes",
            "30m": "30 Minutes",
            "1h": "1 Hour",
            "4h": "4 Hours",
            "1d": "1 Day"
        }
        
        selected = st.selectbox(
            "Timeframe",
            list(timeframes.keys()),
            format_func=lambda x: timeframes[x],
            index=6  # Default to 1d
        )
        
        return selected