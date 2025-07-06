"""
Streamlit UI for Trading Strategy Backtester
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from strategy_manager import StrategyManager
from data_fetcher import DataFetcher
from main import run_backtest
from report_generator import ReportGenerator


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

# Title and description
st.title("🚀 Scalparo - Trading Strategy Backtester")
st.markdown("### Modular, plug-and-play trading strategy testing platform")

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
        with st.spinner("Running backtest..."):
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
                
                # Get strategy class
                strategy_class = st.session_state.strategy_manager.get_strategy(strategy_name)
                
                # Run backtest
                cerebro, results = run_backtest(config, strategy_class, strategy_params)
                
                # Generate report
                report_gen = ReportGenerator(cerebro, results, config)
                report = report_gen.generate_full_report()
                
                st.session_state.backtest_results = {
                    'cerebro': cerebro,
                    'results': results,
                    'report': report,
                    'config': config
                }
                
                st.success("✅ Backtest completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error running backtest: {str(e)}")

# Display results if available
if st.session_state.backtest_results:
    report = st.session_state.backtest_results['report']
    
    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "📈 Metrics", "🤖 AI Insights", "📋 Full Report"])
    
    with tab1:
        st.header("Executive Summary")
        
        # Summary metrics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Return", report['summary']['total_return'])
            st.metric("Final Value", report['summary']['final_value'])
        
        with col2:
            st.metric("Win Rate", report['summary']['win_rate'])
            st.metric("Total Trades", report['summary']['total_trades'])
        
        with col3:
            st.metric("Sharpe Ratio", report['summary']['sharpe_ratio'])
            st.metric("Max Drawdown", report['summary']['max_drawdown'])
    
    with tab2:
        st.header("Detailed Metrics")
        
        # Basic Performance
        st.subheader("💰 Basic Performance")
        basic_perf = report['metrics']['basic_performance']
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Starting Value:** ${basic_perf['starting_value']:,.2f}")
            st.write(f"**Final Value:** ${basic_perf['final_value']:,.2f}")
            st.write(f"**Total Return:** {basic_perf['total_return']:.2f}%")
        with col2:
            st.write(f"**Profit/Loss:** ${basic_perf['total_profit_loss']:,.2f}")
            st.write(f"**Data Period:** {basic_perf['data_period']}")
            st.write(f"**Interval:** {basic_perf['interval']}")
        
        # Risk Metrics
        if 'risk' in report['metrics']:
            st.subheader("📉 Risk Metrics")
            risk = report['metrics']['risk']
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Sharpe Ratio:** {risk['sharpe_ratio']}")
                st.write(f"**Max Drawdown:** {risk['max_drawdown']:.2f}%")
            with col2:
                st.write(f"**Max DD Period:** {risk['max_drawdown_period']} periods")
                st.write(f"**Max DD Money:** ${risk['max_drawdown_money']:,.2f}")
        
        # Trade Analysis
        if 'trades' in report['metrics']:
            st.subheader("🎯 Trade Analysis")
            trades = report['metrics']['trades']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Total Trades:** {trades['total_trades']}")
                st.write(f"**Winning Trades:** {trades['winning_trades']}")
                st.write(f"**Losing Trades:** {trades['losing_trades']}")
            with col2:
                st.write(f"**Win Rate:** {trades['win_rate']:.2f}%")
                st.write(f"**Avg Win:** ${trades['avg_win']:,.2f}")
                st.write(f"**Avg Loss:** ${trades['avg_loss']:,.2f}")
            with col3:
                st.write(f"**Best Trade:** ${trades['best_trade']:,.2f}")
                st.write(f"**Worst Trade:** ${trades['worst_trade']:,.2f}")
                st.write(f"**Max Consec. Wins:** {trades['max_consecutive_wins']}")
    
    with tab3:
        st.header("AI-Powered Insights")
        st.write(report['ai_insights'])
        
        st.subheader("💡 Recommendations")
        for i, rec in enumerate(report['recommendations'], 1):
            st.write(f"{i}. {rec}")
    
    with tab4:
        st.header("Full Report")
        
        # Download button for JSON report
        json_report = json.dumps(report, indent=4)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json_report,
            file_name=f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        # Display full report in expandable section
        with st.expander("View Full Report"):
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
st.markdown("Made with ❤️ by Scalparo | [GitHub](https://github.com/yourusername/scalparo)")