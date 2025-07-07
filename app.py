"""
Enhanced Streamlit UI for Trading Strategy Backtester with Modern SaaS Interface
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from strategy_manager import StrategyManager
from data_fetcher import DataFetcher
from main import run_backtest
from report_generator import ReportGenerator
from chart_components import ChartGenerator
from signal_extractor import SignalExtractor
from performance_analytics import PerformanceAnalyzer
from benchmark_calculator import BenchmarkCalculator

# Page configuration MUST be first
st.set_page_config(
    page_title="Scalparo - Professional Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern SaaS trading interface
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global theme variables */
    :root {
        --primary-bg: #FFFFFF;
        --secondary-bg: #F8F9FA;
        --card-bg: #FFFFFF;
        --accent-bg: #F1F3F4;
        --border-color: #E1E4E8;
        --text-primary: #24292E;
        --text-secondary: #586069;
        --text-muted: #959DA5;
        --accent-color: #0366D6;
        --success-color: #28A745;
        --danger-color: #D73A49;
        --warning-color: #F66A0A;
        --info-color: #0366D6;
    }

    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, var(--primary-bg) 0%, #F5F7FA 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main header */
    .main-header {
        background: linear-gradient(90deg, var(--card-bg) 0%, var(--accent-bg) 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, var(--accent-color), #0052CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .main-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: var(--secondary-bg);
        border-right: 2px solid var(--border-color);
    }

    /* Streamlit sidebar content */
    .css-1lcbmhc {
        background: var(--secondary-bg);
    }

    .sidebar-section {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }

    .sidebar-title {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
        padding-bottom: 0.5rem;
    }

    /* Custom metrics cards */
    .metric-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        text-align: center;
        margin: 0.5rem;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: var(--accent-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(3, 102, 214, 0.15);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-positive { color: var(--success-color); }
    .metric-negative { color: var(--danger-color); }
    .metric-neutral { color: var(--info-color); }

    /* Trading dashboard layout */
    .trading-dashboard {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 1rem;
        margin: 2rem 0;
    }

    /* Chart container */
    .chart-container {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--secondary-bg);
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        border-radius: 6px;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: var(--accent-color);
        color: var(--primary-bg);
        font-weight: 600;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(45deg, var(--accent-color), #0052CC);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(3, 102, 214, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(3, 102, 214, 0.4);
    }

    /* Status indicators */
    .status-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-success {
        background: rgba(2, 192, 118, 0.2);
        color: var(--success-color);
        border: 1px solid var(--success-color);
    }

    .status-danger {
        background: rgba(248, 73, 96, 0.2);
        color: var(--danger-color);
        border: 1px solid var(--danger-color);
    }

    .status-warning {
        background: rgba(255, 143, 0, 0.2);
        color: var(--warning-color);
        border: 1px solid var(--warning-color);
    }

    /* Performance summary */
    .performance-summary {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--accent-bg) 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 2rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    /* Signal badges */
    .signal-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }

    .signal-buy {
        background: rgba(2, 192, 118, 0.2);
        color: var(--success-color);
        border: 1px solid var(--success-color);
    }

    .signal-sell {
        background: rgba(248, 73, 96, 0.2);
        color: var(--danger-color);
        border: 1px solid var(--danger-color);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
        font-weight: 600;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--secondary-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--accent-color);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #FCD434;
    }

    /* Input styling */
    .stSelectbox > div > div {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        color: var(--text-primary);
    }

    .stNumberInput > div > div > input {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        color: var(--text-primary);
    }

    .stTextInput > div > div > input {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        color: var(--text-primary);
    }

    /* Market status */
    .market-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: var(--card-bg);
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }

    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--success-color);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(2, 192, 118, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(2, 192, 118, 0); }
        100% { box-shadow: 0 0 0 0 rgba(2, 192, 118, 0); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'strategy_manager' not in st.session_state:
    st.session_state.strategy_manager = StrategyManager()
    st.session_state.strategy_manager.load_custom_strategies()

if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None

if 'chart_generator' not in st.session_state:
    st.session_state.chart_generator = ChartGenerator()

if 'signal_extractor' not in st.session_state:
    st.session_state.signal_extractor = SignalExtractor()

if 'performance_analyzer' not in st.session_state:
    st.session_state.performance_analyzer = PerformanceAnalyzer()

if 'benchmark_calculator' not in st.session_state:
    st.session_state.benchmark_calculator = BenchmarkCalculator()

# Main header
st.markdown("""
<div class="main-header">
    <div class="main-title">⚡ SCALPARO PRO</div>
    <div class="main-subtitle">Professional Trading Strategy Backtester & Analytics Platform</div>
</div>
""", unsafe_allow_html=True)

# Market status indicator
st.markdown("""
<div class="market-status">
    <div class="status-dot"></div>
    <span style="color: var(--text-primary); font-weight: 600;">System Online</span>
    <span style="color: var(--text-secondary); margin-left: auto;">Last Update: Real-time</span>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration with modern styling
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎯 TRADING CONFIGURATION</div>', unsafe_allow_html=True)

    # Data Configuration
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**📊 Market Data**")

        symbol = st.text_input("Trading Symbol", value="BTC-USD", help="Enter symbol (e.g., BTC-USD, AAPL, TSLA)")

        col1, col2 = st.columns(2)
        with col1:
            default_start, default_end = DataFetcher.get_default_dates()
            start_date = st.date_input("Start", value=pd.to_datetime(default_start))
        with col2:
            end_date = st.date_input("End", value=pd.to_datetime(default_end))

        interval = st.selectbox(
            "Timeframe",
            options=['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1wk', '1mo'],
            index=4
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Trading Configuration
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**💰 Capital Management**")

        initial_capital = st.number_input(
            "Initial Capital ($)",
            min_value=100,
            max_value=1000000,
            value=10000,
            step=1000
        )

        commission = st.slider(
            "Commission (%)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.01
        ) / 100
        st.markdown('</div>', unsafe_allow_html=True)

    # Strategy Selection
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🚀 Strategy Engine**")

        available_strategies = st.session_state.strategy_manager.get_all_strategies()
        strategy_name = st.selectbox(
            "Strategy",
            options=list(available_strategies.keys())
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Strategy Parameters
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**⚙️ Strategy Parameters**")

        strategy_params = {}
        param_config = st.session_state.strategy_manager.get_strategy_params(strategy_name)

        if param_config:
            for param_name, param_info in param_config.items():
                if param_info['type'] == 'int':
                    value = st.number_input(
                        param_info['description'],
                        min_value=param_info.get('min', 1),
                        max_value=param_info.get('max', 100),
                        value=param_info['default'],
                        key=f"param_{param_name}"
                    )
                    strategy_params[param_name] = int(value)
                elif param_info['type'] == 'float':
                    value = st.slider(
                        param_info['description'],
                        min_value=float(param_info.get('min', 0.0)),
                        max_value=float(param_info.get('max', 10.0)),
                        value=float(param_info['default']),
                        step=float(param_info.get('step', 0.1)),
                        key=f"param_{param_name}"
                    )
                    strategy_params[param_name] = value
        st.markdown('</div>', unsafe_allow_html=True)

    # Execute button
    st.markdown("---")
    run_backtest_btn = st.button("🚀 EXECUTE BACKTEST", use_container_width=True)

# Main dashboard
if run_backtest_btn:
    with st.spinner("🔄 Running comprehensive analysis..."):
        try:
            # Configuration
            config = {
                'symbol': symbol,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'interval': interval,
                'initial_capital': initial_capital,
                'commission': commission,
                'strategy_name': strategy_name,
                'strategy_params': strategy_params
            }

            # Fetch data
            data = DataFetcher.fetch_yahoo_data(
                symbol, interval, config['start_date'], config['end_date']
            )

            if data.empty:
                st.error("❌ Unable to fetch market data. This could be due to:")
                st.error("• Network restrictions or connectivity issues")
                st.error("• API service unavailability") 
                st.error("• Invalid symbol or date range")
                st.info("💡 Please check your internet connection and try again later.")
                st.stop()

            if not DataFetcher.validate_data(data):
                st.error("❌ Invalid data received. Please try different parameters.")
                st.stop()

            strategy_class = st.session_state.strategy_manager.get_strategy(strategy_name)
            cerebro, results = run_backtest(config, strategy_class, strategy_params)

            # Generate reports
            report_gen = ReportGenerator(cerebro, results, config)
            report = report_gen.generate_full_report()

            # Extract signals and analytics
            signals = st.session_state.signal_extractor.extract_from_backtest(cerebro, results)
            formatted_signals = st.session_state.signal_extractor.format_for_plotting(signals)

            performance_analysis = st.session_state.performance_analyzer.analyze_backtest_results(
                cerebro, results, data
            )

            benchmark_report = st.session_state.benchmark_calculator.create_benchmark_report(
                report['metrics']['basic_performance'], symbol, 
                config['start_date'], config['end_date']
            )

            st.session_state.backtest_results = {
                'cerebro': cerebro,
                'results': results,
                'report': report,
                'config': config,
                'data': data,
                'signals': signals,
                'formatted_signals': formatted_signals,
                'performance_analysis': performance_analysis,
                'benchmark_report': benchmark_report
            }

            st.success("✅ Analysis completed successfully!")

        except Exception as e:
            st.error(f"❌ Execution failed: {str(e)}")

# Display results if available
if st.session_state.backtest_results:
    results_data = st.session_state.backtest_results
    report = results_data['report']
    performance_analysis = results_data['performance_analysis']
    benchmark_report = results_data['benchmark_report']
    signals = results_data['formatted_signals']

    # Performance summary dashboard
    st.markdown('<div class="performance-summary">', unsafe_allow_html=True)

    basic_perf = report['metrics']['basic_performance']
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_return = basic_perf['total_return']
        color_class = "metric-positive" if total_return > 0 else "metric-negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {color_class}">{total_return:.2f}%</div>
            <div class="metric-label">Total Return</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        final_value = basic_perf['final_value']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value metric-neutral">${final_value:,.0f}</div>
            <div class="metric-label">Portfolio Value</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if 'risk' in report['metrics'] and 'sharpe_ratio' in report['metrics']['risk']:
            sharpe = report['metrics']['risk']['sharpe_ratio']
            if sharpe is not None:
                color_class = "metric-positive" if sharpe > 1 else "metric-warning" if sharpe > 0 else "metric-negative"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value {color_class}">{sharpe:.2f}</div>
                    <div class="metric-label">Sharpe Ratio</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value metric-neutral">N/A</div>
                    <div class="metric-label">Sharpe Ratio</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value metric-neutral">N/A</div>
                <div class="metric-label">Sharpe Ratio</div>
            </div>
            """, unsafe_allow_html=True)

    with col4:
        if 'risk' in report['metrics'] and 'max_drawdown' in report['metrics']['risk']:
            max_dd = report['metrics']['risk']['max_drawdown']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value metric-negative">{max_dd:.2f}%</div>
                <div class="metric-label">Max Drawdown</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value metric-neutral">N/A</div>
                <div class="metric-label">Max Drawdown</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Trading signals summary
    if signals:
        st.markdown("### 📊 Signal Analysis")
        signal_col1, signal_col2, signal_col3, signal_col4 = st.columns(4)

        with signal_col1:
            buy_count = len(signals.get('buy_signals', []))
            st.markdown(f'<span class="signal-badge signal-buy">🟢 {buy_count} Buy Signals</span>', unsafe_allow_html=True)

        with signal_col2:
            sell_count = len(signals.get('sell_signals', []))
            st.markdown(f'<span class="signal-badge signal-sell">🔴 {sell_count} Sell Signals</span>', unsafe_allow_html=True)

        with signal_col3:
            total_trades = len(results_data['signals']['trades'])
            st.markdown(f'<span class="signal-badge" style="background: rgba(24, 144, 255, 0.2); color: var(--info-color); border: 1px solid var(--info-color);">📈 {total_trades} Total Trades</span>', unsafe_allow_html=True)

        with signal_col4:
            if total_trades > 0:
                win_rate = len([t for t in results_data['signals']['trades'] if t.get('result') == 'win']) / total_trades * 100
                color = "var(--success-color)" if win_rate > 50 else "var(--warning-color)" if win_rate > 30 else "var(--danger-color)"
                st.markdown(f'<span class="signal-badge" style="background: rgba(240, 185, 11, 0.2); color: var(--accent-color); border: 1px solid var(--accent-color);">🎯 {win_rate:.1f}% Win Rate</span>', unsafe_allow_html=True)

        # Execution price summary
        execution_prices = results_data['signals'].get('execution_prices', {})
        if execution_prices.get('total_executions', 0) > 0:
            st.markdown("### 💰 Execution Price Analysis")
            exec_col1, exec_col2, exec_col3, exec_col4 = st.columns(4)
            
            with exec_col1:
                avg_buy = execution_prices.get('average_buy_price', 0)
                if avg_buy > 0:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value metric-positive">${avg_buy:,.2f}</div>
                        <div class="metric-label">Avg Buy Price</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with exec_col2:
                avg_sell = execution_prices.get('average_sell_price', 0)
                if avg_sell > 0:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value metric-negative">${avg_sell:,.2f}</div>
                        <div class="metric-label">Avg Sell Price</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with exec_col3:
                buy_executions = len(execution_prices.get('buy_executions', []))
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value metric-neutral">{buy_executions}</div>
                    <div class="metric-label">Buy Executions</div>
                </div>
                """, unsafe_allow_html=True)
            
            with exec_col4:
                sell_executions = len(execution_prices.get('sell_executions', []))
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value metric-neutral">{sell_executions}</div>
                    <div class="metric-label">Sell Executions</div>
                </div>
                """, unsafe_allow_html=True)

    # Enhanced tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Live Chart", 
        "📊 Performance Analytics", 
        "🎯 Advanced Metrics",
        "🤖 AI Intelligence", 
        "📋 Complete Report"
    ])

    with tab1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📈 Interactive Trading Chart")

        # Chart controls
        chart_col1, chart_col2, chart_col3 = st.columns([2, 2, 1])

        with chart_col1:
            chart_interval = st.selectbox(
                "Chart Timeframe",
                options=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                index=4,
                key="chart_interval"
            )

        with chart_col2:
            show_volume = st.checkbox("Volume", value=True)
            show_signals = st.checkbox("Signals", value=True)

        with chart_col3:
            signal_count = len(signals.get('buy_signals', [])) + len(signals.get('sell_signals', []))
            st.metric("Signals", signal_count)

        # Create chart
        try:
            chart_signals = signals if show_signals else None
            candlestick_fig = st.session_state.chart_generator.create_candlestick_chart(
                results_data['data'], chart_signals
            )
            candlestick_fig.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='#24292E')
            )
            st.plotly_chart(candlestick_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📊 Strategy Performance Analytics")

        # Comparison with benchmark
        if benchmark_report and 'benchmark_performance' in benchmark_report:
            st.markdown("#### 🎯 Strategy vs Buy & Hold")

            bench_col1, bench_col2 = st.columns(2)

            with bench_col1:
                st.markdown("**Strategy Performance**")
                st.metric("Return", f"{basic_perf['total_return']:.2f}%")
                st.metric("Final Value", f"${basic_perf['final_value']:,.0f}")

            with bench_col2:
                st.markdown("**Buy & Hold Benchmark**")
                benchmark_perf = benchmark_report['benchmark_performance']
                st.metric("Return", f"{benchmark_perf['total_return']:.2f}%")
                st.metric("Final Value", f"${benchmark_perf['final_value']:,.0f}")

        # Additional analytics charts
        if performance_analysis:
            try:
                # Price distribution
                histogram_fig = st.session_state.chart_generator.create_price_histogram(results_data['data'])
                histogram_fig.update_layout(
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(color='#24292E')
                )
                st.plotly_chart(histogram_fig, use_container_width=True)

                # Drawdown analysis
                if 'returns' in performance_analysis:
                    drawdown_fig = st.session_state.chart_generator.create_drawdown_chart(
                        performance_analysis['returns']
                    )
                    drawdown_fig.update_layout(
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        font=dict(color='#24292E')
                    )
                    st.plotly_chart(drawdown_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Analytics error: {str(e)}")

    with tab3:
        st.markdown("### 🎯 Advanced Performance Metrics")

        if performance_analysis:
            # Advanced metrics grid
            if 'risk_metrics' in performance_analysis:
                st.markdown("#### 📊 Risk Analysis")
                risk = performance_analysis['risk_metrics']

                risk_col1, risk_col2, risk_col3 = st.columns(3)
                with risk_col1:
                    st.metric("Volatility", f"{risk.get('volatility', 0):.2f}%")
                    st.metric("VaR (95%)", f"{risk.get('value_at_risk_95', 0):.2f}%")

                with risk_col2:
                    st.metric("Sortino Ratio", f"{risk.get('sortino_ratio', 0):.2f}")
                    st.metric("Calmar Ratio", f"{risk.get('calmar_ratio', 0):.2f}")

                with risk_col3:
                    st.metric("Expected Shortfall", f"{risk.get('expected_shortfall_95', 0):.2f}%")

            # Trade analysis
            if 'trade_metrics' in performance_analysis:
                st.markdown("#### 🎯 Trade Analysis")
                trades = performance_analysis['trade_metrics']

                trade_col1, trade_col2, trade_col3 = st.columns(3)
                with trade_col1:
                    st.metric("Win Rate", f"{trades.get('win_rate', 0):.1f}%")
                    st.metric("Avg Win", f"${trades.get('avg_win', 0):.2f}")

                with trade_col2:
                    st.metric("Avg Loss", f"${trades.get('avg_loss', 0):.2f}")
                    st.metric("Profit Factor", f"{trades.get('profit_factor', 0):.2f}")

                with trade_col3:
                    st.metric("Best Trade", f"${trades.get('best_trade', 0):.2f}")
                    st.metric("Worst Trade", f"${trades.get('worst_trade', 0):.2f}")

            # Execution price details
            execution_prices = results_data['signals'].get('execution_prices', {})
            if execution_prices.get('total_executions', 0) > 0:
                st.markdown("#### 💱 Execution Price Details")
                
                exec_detail_col1, exec_detail_col2 = st.columns(2)
                
                with exec_detail_col1:
                    st.markdown("**Buy Executions**")
                    buy_executions = execution_prices.get('buy_executions', [])
                    if buy_executions:
                        buy_df = pd.DataFrame({
                            'Execution #': range(1, len(buy_executions) + 1),
                            'Price': [f"${price:,.2f}" for price in buy_executions]
                        })
                        st.dataframe(buy_df, use_container_width=True)
                        
                        # Buy price statistics
                        st.markdown("**Buy Price Stats**")
                        st.metric("Highest Buy", f"${max(buy_executions):,.2f}")
                        st.metric("Lowest Buy", f"${min(buy_executions):,.2f}")
                        st.metric("Price Range", f"${max(buy_executions) - min(buy_executions):,.2f}")
                
                with exec_detail_col2:
                    st.markdown("**Sell Executions**")
                    sell_executions = execution_prices.get('sell_executions', [])
                    if sell_executions:
                        sell_df = pd.DataFrame({
                            'Execution #': range(1, len(sell_executions) + 1),
                            'Price': [f"${price:,.2f}" for price in sell_executions]
                        })
                        st.dataframe(sell_df, use_container_width=True)
                        
                        # Sell price statistics
                        st.markdown("**Sell Price Stats**")
                        st.metric("Highest Sell", f"${max(sell_executions):,.2f}")
                        st.metric("Lowest Sell", f"${min(sell_executions):,.2f}")
                        st.metric("Price Range", f"${max(sell_executions) - min(sell_executions):,.2f}")

        # Trade timeline
        if results_data['signals']['trades']:
            try:
                trade_timeline_fig = st.session_state.chart_generator.create_trade_timeline(
                    results_data['signals']['trades']
                )
                trade_timeline_fig.update_layout(
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(color='#24292E')
                )
                st.plotly_chart(trade_timeline_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Timeline error: {str(e)}")

    with tab4:
        st.markdown("### 🤖 AI-Powered Intelligence")

        # AI insights with modern styling
        st.markdown(f"""
        <div style="background: var(--card-bg); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color); margin: 1rem 0;">
            <h4 style="color: var(--accent-color); margin-bottom: 1rem;">💡 AI Analysis</h4>
            <p style="color: var(--text-primary); line-height: 1.6;">{report['ai_insights']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Recommendations
        st.markdown("#### 📋 Strategic Recommendations")
        for i, rec in enumerate(report['recommendations'], 1):
            st.markdown(f"""
            <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-color); margin: 0.5rem 0;">
                <span style="color: var(--text-primary);">{i}. {rec}</span>
            </div>
            """, unsafe_allow_html=True)

        # Benchmark recommendations
        if benchmark_report and 'recommendations' in benchmark_report:
            st.markdown("#### 📊 Benchmark Analysis")
            for i, rec in enumerate(benchmark_report['recommendations'], 1):
                st.markdown(f"""
                <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--info-color); margin: 0.5rem 0;">
                    <span style="color: var(--text-primary);">{i}. {rec}</span>
                </div>
                """, unsafe_allow_html=True)

    with tab5:
        st.markdown("### 📋 Complete Analysis Report")

        # Download section
        download_col1, download_col2 = st.columns(2)

        with download_col1:
            json_report = json.dumps(report, indent=4)
            st.download_button(
                label="📥 Download Basic Report",
                data=json_report,
                file_name=f"scalparo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        with download_col2:
            enhanced_report = {
                'basic_report': report,
                'performance_analysis': performance_analysis,
                'benchmark_analysis': benchmark_report,
                'signals_summary': results_data['signals']
            }
            enhanced_json = json.dumps(enhanced_report, indent=4, default=str)
            st.download_button(
                label="📥 Download Enhanced Report",
                data=enhanced_json,
                file_name=f"scalparo_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        # Expandable report sections
        with st.expander("📊 Performance Analysis Details"):
            if performance_analysis:
                st.json(performance_analysis)

        with st.expander("📈 Benchmark Comparison"):
            if benchmark_report:
                st.json(benchmark_report)

        with st.expander("🎯 Trading Signals"):
            st.json(results_data['signals'])

        with st.expander("📋 Complete Report Data"):
            st.json(report)

# Strategy creation section
with st.expander("🛠️ Strategy Development Lab"):
    st.markdown("### 🧪 Create Custom Strategy")

    new_strategy_name = st.text_input("Strategy Name", placeholder="e.g., MyAdvancedStrategy")

    if st.button("🚀 Generate Strategy Template"):
        if new_strategy_name:
            try:
                filename = st.session_state.strategy_manager.create_custom_strategy_template(new_strategy_name)
                st.success(f"✅ Strategy template created: {filename}")
                st.info("💡 Edit the generated file to implement your strategy logic, then restart to use it.")
            except Exception as e:
                st.error(f"❌ Creation failed: {str(e)}")
        else:
            st.warning("⚠️ Please enter a strategy name")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: var(--text-muted);">
    <p><strong>SCALPARO PRO</strong> | Professional Trading Analytics Platform</p>
    <p>Powered by Advanced AI & Real-time Market Data</p>
</div>
""", unsafe_allow_html=True)