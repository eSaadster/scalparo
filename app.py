"""
Enhanced Streamlit UI for Trading Strategy Backtester with Interactive Charts
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


st.set_page_config(
    page_title="Scalparo - Trading Strategy Backtester",
    page_icon="📈",
    layout="wide"
)

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

# Title and description
st.title("🚀 Scalparo - Enhanced Trading Strategy Backtester")
st.markdown("### Professional-grade trading analytics with interactive charts and advanced performance analysis")

# Sidebar for configuration
with st.sidebar:
    st.header("📊 Configuration")
    
    # Data Configuration
    st.subheader("1. Data Settings")
    
    symbol = st.text_input("Symbol", value="BTC-USD", help="Trading symbol (e.g., BTC-USD, AAPL)")
    
    col1, col2 = st.columns(2)
    with col1:
        default_start, default_end = DataFetcher.get_default_dates()
        start_date = st.date_input("Start Date", value=pd.to_datetime(default_start))
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(default_end))
    
    interval = st.selectbox(
        "Interval",
        options=['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1wk', '1mo'],
        index=4  # Default to 1h
    )
    
    # Trading Configuration
    st.subheader("2. Trading Settings")
    
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
    
    # Strategy Selection
    st.subheader("3. Strategy Selection")
    
    available_strategies = st.session_state.strategy_manager.get_all_strategies()
    strategy_name = st.selectbox(
        "Select Strategy",
        options=list(available_strategies.keys())
    )
    
    # Strategy Parameters
    st.subheader("4. Strategy Parameters")
    
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
    
    # Run Backtest Button
    run_backtest_btn = st.button("🚀 Run Backtest", type="primary", use_container_width=True)

# Main content area
main_container = st.container()

with main_container:
    if run_backtest_btn:
        with st.spinner("Running comprehensive backtest analysis..."):
            try:
                # Prepare configuration
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
                
                # Fetch original data for charts
                data = DataFetcher.fetch_yahoo_data(
                    symbol, interval, config['start_date'], config['end_date']
                )
                
                # Get strategy class
                strategy_class = st.session_state.strategy_manager.get_strategy(strategy_name)
                
                # Run backtest
                cerebro, results = run_backtest(config, strategy_class, strategy_params)
                
                # Generate original report
                report_gen = ReportGenerator(cerebro, results, config)
                report = report_gen.generate_full_report()
                
                # Extract signals
                signals = st.session_state.signal_extractor.extract_from_backtest(cerebro, results)
                formatted_signals = st.session_state.signal_extractor.format_for_plotting(signals)
                
                # Perform advanced analytics
                performance_analysis = st.session_state.performance_analyzer.analyze_backtest_results(
                    cerebro, results, data
                )
                
                # Calculate benchmark comparison
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
                
                st.success("✅ Enhanced backtest analysis completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error running backtest: {str(e)}")
                st.exception(e)

# Display enhanced results if available
if st.session_state.backtest_results:
    data = st.session_state.backtest_results['data']
    signals = st.session_state.backtest_results['formatted_signals']
    report = st.session_state.backtest_results['report']
    performance_analysis = st.session_state.backtest_results['performance_analysis']
    benchmark_report = st.session_state.backtest_results['benchmark_report']
    
    # Enhanced results tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Interactive Chart", 
        "📊 Performance Analysis", 
        "📋 Enhanced Metrics",
        "🤖 AI Insights", 
        "📋 Full Report"
    ])
    
    with tab1:
        st.header("📈 Interactive Trading Chart")
        
        # Interval selector for chart
        st.subheader("Chart Controls")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            chart_interval = st.selectbox(
                "Chart Timeframe",
                options=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                index=4,  # Default to 1h
                key="chart_interval"
            )
        
        with col2:
            show_volume = st.checkbox("Show Volume", value=True)
            show_signals = st.checkbox("Show Trading Signals", value=True)
        
        with col3:
            st.metric("Total Signals", len(signals.get('buy_signals', [])) + len(signals.get('sell_signals', [])))
        
        # Create candlestick chart
        try:
            chart_signals = signals if show_signals else None
            candlestick_fig = st.session_state.chart_generator.create_candlestick_chart(
                data, chart_signals
            )
            st.plotly_chart(candlestick_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
            st.write("Chart data preview:")
            st.dataframe(data.head())
        
        # Signal summary
        if signals:
            st.subheader("📊 Signal Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Buy Signals", len(signals.get('buy_signals', [])))
            with col2:
                st.metric("Sell Signals", len(signals.get('sell_signals', [])))
            with col3:
                total_trades = len(st.session_state.backtest_results['signals']['trades'])
                st.metric("Total Trades", total_trades)
            with col4:
                if total_trades > 0:
                    win_rate = len([t for t in st.session_state.backtest_results['signals']['trades'] 
                                  if t.get('result') == 'win']) / total_trades * 100
                    st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with tab2:
        st.header("📊 Strategy Performance Analysis")
        
        # Price Distribution
        st.subheader("💰 Price Distribution Analysis")
        try:
            histogram_fig = st.session_state.chart_generator.create_price_histogram(data)
            st.plotly_chart(histogram_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating histogram: {str(e)}")
        
        # Strategy vs Benchmark Comparison
        st.subheader("🎯 Strategy vs Buy & Hold Comparison")
        
        if benchmark_report and 'benchmark_performance' in benchmark_report:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Strategy Performance")
                basic_perf = report['metrics']['basic_performance']
                st.metric("Total Return", f"{basic_perf['total_return']:.2f}%")
                st.metric("Final Value", f"${basic_perf['final_value']:,.2f}")
                if 'risk' in report['metrics']:
                    st.metric("Sharpe Ratio", f"{report['metrics']['risk']['sharpe_ratio']}")
                    st.metric("Max Drawdown", f"{report['metrics']['risk']['max_drawdown']:.2f}%")
            
            with col2:
                st.subheader("Buy & Hold Benchmark")
                benchmark_perf = benchmark_report['benchmark_performance']
                st.metric("Total Return", f"{benchmark_perf['total_return']:.2f}%")
                st.metric("Final Value", f"${benchmark_perf['final_value']:,.2f}")
                st.metric("Sharpe Ratio", f"{benchmark_perf['sharpe_ratio']:.2f}")
                st.metric("Max Drawdown", f"{benchmark_perf['max_drawdown']:.2f}%")
            
            # Comparison chart
            if 'comparison_analysis' in benchmark_report:
                comparison = benchmark_report['comparison_analysis']
                st.subheader("📈 Performance Comparison")
                
                # Create comparison metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    excess_return = comparison.get('excess_return', 0)
                    st.metric("Excess Return", f"{excess_return:.2f}%", 
                             f"{excess_return:.2f}%")
                with col2:
                    sharpe_diff = comparison.get('sharpe_difference', 0)
                    st.metric("Sharpe Difference", f"{sharpe_diff:.2f}", 
                             f"{sharpe_diff:.2f}")
                with col3:
                    info_ratio = comparison.get('information_ratio', 0)
                    st.metric("Information Ratio", f"{info_ratio:.2f}")
                
                # Summary
                if 'summary' in benchmark_report:
                    st.info(benchmark_report['summary'])
        
        # Rolling Performance Metrics
        st.subheader("📈 Rolling Performance Metrics")
        if performance_analysis and 'rolling_metrics' in performance_analysis:
            try:
                rolling_window = st.slider("Rolling Window (days)", 10, 60, 30)
                rolling_fig = st.session_state.chart_generator.create_rolling_metrics_chart(
                    performance_analysis['returns'], rolling_window
                )
                st.plotly_chart(rolling_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating rolling metrics chart: {str(e)}")
        
        # Drawdown Analysis
        st.subheader("📉 Drawdown Analysis")
        if performance_analysis and 'returns' in performance_analysis:
            try:
                drawdown_fig = st.session_state.chart_generator.create_drawdown_chart(
                    performance_analysis['returns']
                )
                st.plotly_chart(drawdown_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating drawdown chart: {str(e)}")
    
    with tab3:
        st.header("📋 Enhanced Performance Metrics")
        
        # Advanced Metrics Grid
        st.subheader("🎯 Advanced Performance Metrics")
        
        if performance_analysis:
            # Basic Performance
            if 'basic_metrics' in performance_analysis:
                st.subheader("💰 Basic Performance")
                basic = performance_analysis['basic_metrics']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Return", f"{basic.get('total_return', 0):.2f}%")
                    st.metric("Annualized Return", f"{basic.get('annualized_return', 0):.2f}%")
                with col2:
                    st.metric("Final Value", f"${basic.get('final_value', 0):,.2f}")
                    st.metric("Total P&L", f"${basic.get('total_profit_loss', 0):,.2f}")
                with col3:
                    st.metric("Days Traded", f"{basic.get('days_traded', 0)}")
                    st.metric("Initial Capital", f"${basic.get('initial_value', 0):,.2f}")
            
            # Risk Metrics
            if 'risk_metrics' in performance_analysis:
                st.subheader("📊 Risk Analysis")
                risk = performance_analysis['risk_metrics']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Volatility", f"{risk.get('volatility', 0):.2f}%")
                    st.metric("Sharpe Ratio", f"{risk.get('sharpe_ratio', 0):.2f}")
                with col2:
                    st.metric("Max Drawdown", f"{risk.get('max_drawdown', 0):.2f}%")
                    st.metric("Calmar Ratio", f"{risk.get('calmar_ratio', 0):.2f}")
                with col3:
                    st.metric("Sortino Ratio", f"{risk.get('sortino_ratio', 0):.2f}")
                    st.metric("VaR (95%)", f"{risk.get('value_at_risk_95', 0):.2f}%")
                with col4:
                    st.metric("Expected Shortfall", f"{risk.get('expected_shortfall_95', 0):.2f}%")
            
            # Trade Analysis
            if 'trade_metrics' in performance_analysis:
                st.subheader("🎯 Trade Analysis")
                trades = performance_analysis['trade_metrics']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Trades", trades.get('total_trades', 0))
                    st.metric("Win Rate", f"{trades.get('win_rate', 0):.2f}%")
                with col2:
                    st.metric("Winning Trades", trades.get('winning_trades', 0))
                    st.metric("Average Win", f"${trades.get('avg_win', 0):.2f}")
                with col3:
                    st.metric("Losing Trades", trades.get('losing_trades', 0))
                    st.metric("Average Loss", f"${trades.get('avg_loss', 0):.2f}")
                with col4:
                    st.metric("Profit Factor", f"{trades.get('profit_factor', 0):.2f}")
                    st.metric("Best Trade", f"${trades.get('best_trade', 0):.2f}")
        
        # Trade Timeline
        st.subheader("📈 Trade Timeline")
        if st.session_state.backtest_results['signals']['trades']:
            try:
                trade_timeline_fig = st.session_state.chart_generator.create_trade_timeline(
                    st.session_state.backtest_results['signals']['trades']
                )
                st.plotly_chart(trade_timeline_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating trade timeline: {str(e)}")
        else:
            st.info("No trade data available for timeline visualization.")
        
        # Monthly Performance Analysis
        if performance_analysis and 'monthly_analysis' in performance_analysis:
            st.subheader("📅 Monthly Performance Analysis")
            monthly = performance_analysis['monthly_analysis']
            
            if 'monthly_stats' in monthly:
                stats = monthly['monthly_stats']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Best Month", f"{stats.get('best_month', 0):.2f}%")
                with col2:
                    st.metric("Worst Month", f"{stats.get('worst_month', 0):.2f}%")
                with col3:
                    st.metric("Positive Months", stats.get('positive_months', 0))
                with col4:
                    st.metric("Negative Months", stats.get('negative_months', 0))
        
        # Risk-Return Scatter
        st.subheader("📊 Risk-Return Analysis")
        if benchmark_report and 'benchmark_performance' in benchmark_report:
            try:
                strategy_data = {
                    'return': report['metrics']['basic_performance']['total_return'],
                    'volatility': performance_analysis.get('risk_metrics', {}).get('volatility', 0),
                    'sharpe': performance_analysis.get('risk_metrics', {}).get('sharpe_ratio', 0)
                }
                benchmark_data = {
                    'return': benchmark_report['benchmark_performance']['total_return'],
                    'volatility': benchmark_report['benchmark_performance']['volatility'],
                    'sharpe': benchmark_report['benchmark_performance']['sharpe_ratio']
                }
                
                risk_return_fig = st.session_state.chart_generator.create_risk_return_scatter(
                    strategy_data, benchmark_data
                )
                st.plotly_chart(risk_return_fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating risk-return scatter: {str(e)}")
    
    with tab4:
        st.header("🤖 AI-Powered Insights")
        st.write(report['ai_insights'])
        
        st.subheader("💡 Recommendations")
        for i, rec in enumerate(report['recommendations'], 1):
            st.write(f"{i}. {rec}")
        
        # Enhanced recommendations from benchmark analysis
        if benchmark_report and 'recommendations' in benchmark_report:
            st.subheader("📊 Benchmark-Based Recommendations")
            for i, rec in enumerate(benchmark_report['recommendations'], 1):
                st.write(f"{i}. {rec}")
    
    with tab5:
        st.header("📋 Complete Analysis Report")
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Original JSON report
            json_report = json.dumps(report, indent=4)
            st.download_button(
                label="📥 Download Basic Report (JSON)",
                data=json_report,
                file_name=f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Enhanced analysis report
            enhanced_report = {
                'basic_report': report,
                'performance_analysis': performance_analysis,
                'benchmark_analysis': benchmark_report,
                'signals_summary': st.session_state.backtest_results['signals']
            }
            enhanced_json = json.dumps(enhanced_report, indent=4, default=str)
            st.download_button(
                label="📥 Download Enhanced Report (JSON)",
                data=enhanced_json,
                file_name=f"enhanced_trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Display reports in expandable sections
        with st.expander("📊 Performance Analysis Details"):
            if performance_analysis:
                st.json(performance_analysis)
        
        with st.expander("📈 Benchmark Comparison Details"):
            if benchmark_report:
                st.json(benchmark_report)
        
        with st.expander("🎯 Trading Signals Details"):
            st.json(st.session_state.backtest_results['signals'])
        
        with st.expander("📋 Original Report"):
            st.json(report)

# Custom Strategy Creation Section
with st.expander("🛠️ Create Custom Strategy"):
    st.subheader("Create Your Own Strategy")
    
    new_strategy_name = st.text_input("Strategy Name (e.g., MyCustom)")
    
    if st.button("Generate Strategy Template"):
        if new_strategy_name:
            try:
                filename = st.session_state.strategy_manager.create_custom_strategy_template(new_strategy_name)
                st.success(f"✅ Strategy template created: {filename}")
                st.info("Edit the file to implement your strategy logic, then restart the app to use it.")
            except Exception as e:
                st.error(f"Error creating strategy: {str(e)}")
        else:
            st.warning("Please enter a strategy name")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Scalparo | Enhanced with Interactive Charts & Advanced Analytics")