"""
Real-Time Crypto Analytics Dashboard
Main Streamlit application
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import threading

# Import our modules
from backend.database import init_database, get_recent_data, get_tick_count
from backend.websocket_client import BinanceWebSocketClient
from backend.data_processor import DataProcessor
from analytics.statistics import TradingAnalytics
from analytics.alerts import AlertManager, create_default_alerts

# Page config
st.set_page_config(
    page_title="Crypto Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'websocket_started' not in st.session_state:
    st.session_state.websocket_started = False
if 'alert_manager' not in st.session_state:
    st.session_state.alert_manager = create_default_alerts()

# Initialize database
init_database()

# Sidebar controls
st.sidebar.title("⚙️ Controls")

# Symbol selection
symbols = st.sidebar.multiselect(
    "Select Symbols",
    ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"],
    default=["BTCUSDT", "ETHUSDT"]
)

# Timeframe selection
timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1s", "5s", "10s", "30s", "1min", "5min"],
    index=4
)

# Window sizes
zscore_window = st.sidebar.slider("Z-Score Window", 10, 100, 20)
corr_window = st.sidebar.slider("Correlation Window", 10, 100, 20)

# Data refresh
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 2)

# Main title
st.title("🚀 Real-Time Crypto Analytics Dashboard")
st.markdown("---")

# WebSocket control
col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    if st.button("🟢 Start WebSocket" if not st.session_state.websocket_started else "🔴 Stop WebSocket"):
        if not st.session_state.websocket_started:
            # Start WebSocket in background
            st.session_state.websocket_started = True
            st.success("✅ WebSocket started!")
            st.rerun()
        else:
            st.session_state.websocket_started = False
            st.info("⏸️ WebSocket stopped")
            st.rerun()

with col2:
    status = "🟢 LIVE" if st.session_state.websocket_started else "🔴 STOPPED"
    st.metric("Status", status)

with col3:
    total_ticks = sum([get_tick_count(sym) for sym in symbols])
    st.metric("Total Ticks", f"{total_ticks:,}")

st.markdown("---")

# Main dashboard
if len(symbols) == 0:
    st.warning("⚠️ Please select at least one symbol from the sidebar")
    st.stop()

# Analytics objects
processor = DataProcessor()
analytics = TradingAnalytics()

# Create tabs
if len(symbols) == 1:
    tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "📊 Statistics", "🚨 Alerts"])
else:
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Charts", "📊 Spread Analysis", "📉 Statistics", "🚨 Alerts"])

# Tab 1: Price Charts
with tab1:
    st.subheader("Live Price Data")
    
    chart_cols = st.columns(len(symbols))
    
    for idx, symbol in enumerate(symbols):
        with chart_cols[idx]:
            # Get data
            df = get_recent_data(symbol, limit=500)
            
            if not df.empty:
                # Resample to OHLCV
                ohlcv = processor.resample_dataframe(df, timeframe)
                
                if not ohlcv.empty:
                    # Create candlestick chart
                    fig = go.Figure(data=[go.Candlestick(
                        x=ohlcv['datetime'],
                        open=ohlcv['open'],
                        high=ohlcv['high'],
                        low=ohlcv['low'],
                        close=ohlcv['close'],
                        name=symbol
                    )])
                    
                    fig.update_layout(
                        title=f"{symbol} Price",
                        xaxis_title="Time",
                        yaxis_title="Price (USD)",
                        height=400,
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Current stats
                    current_price = ohlcv['close'].iloc[-1]
                    price_change = ((current_price - ohlcv['open'].iloc[0]) / ohlcv['open'].iloc[0]) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Current", f"${current_price:,.2f}")
                    col2.metric("Change", f"{price_change:+.2f}%")
                    col3.metric("Ticks", get_tick_count(symbol))
                else:
                    st.info(f"⏳ Waiting for {symbol} data...")
            else:
                st.info(f"⏳ No data yet for {symbol}")

# Tab 2: Spread Analysis (if 2 symbols)
if len(symbols) == 2:
    with tab2:
        st.subheader("Pairs Trading Analysis")
        
        # Get data for both symbols
        df1 = get_recent_data(symbols[0], limit=500)
        df2 = get_recent_data(symbols[1], limit=500)
        
        if not df1.empty and not df2.empty:
            # Resample both
            ohlcv1 = processor.resample_dataframe(df1, timeframe)
            ohlcv2 = processor.resample_dataframe(df2, timeframe)
            
            if not ohlcv1.empty and not ohlcv2.empty:
                # Align timestamps
                merged = pd.merge(ohlcv1[['datetime', 'close']], ohlcv2[['datetime', 'close']], 
                                on='datetime', suffixes=('_1', '_2'))
                
                if len(merged) > 2:
                    # Calculate hedge ratio
                    hedge = analytics.calculate_hedge_ratio(merged['close_1'], merged['close_2'])
                    
                    # Calculate spread
                    spread = analytics.calculate_spread(merged['close_1'], merged['close_2'], hedge['hedge_ratio'])
                    
                    # Calculate z-score
                    zscore = analytics.calculate_zscore(spread, window=min(zscore_window, len(spread)))
                    
                    # Display hedge ratio
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Hedge Ratio", f"{hedge['hedge_ratio']:.4f}")
                    col2.metric("R²", f"{hedge['r_squared']:.4f}")
                    if not zscore.empty:
                        col3.metric("Current Z-Score", f"{zscore.iloc[-1]:.2f}")
                    
                    # Plot spread and z-score
                    fig = make_subplots(rows=2, cols=1, 
                                      subplot_titles=('Spread', 'Z-Score'),
                                      vertical_spacing=0.1)
                    
                    fig.add_trace(go.Scatter(x=merged['datetime'], y=spread, 
                                           name='Spread', line=dict(color='cyan')), 
                                row=1, col=1)
                    
                    if not zscore.empty:
                        fig.add_trace(go.Scatter(x=merged['datetime'], y=zscore, 
                                               name='Z-Score', line=dict(color='orange')), 
                                    row=2, col=1)
                        
                        # Add threshold lines
                        fig.add_hline(y=2, line_dash="dash", line_color="red", row=2, col=1)
                        fig.add_hline(y=-2, line_dash="dash", line_color="green", row=2, col=1)
                    
                    fig.update_layout(height=600, template="plotly_dark", showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # ADF Test
                    st.subheader("Stationarity Test")
                    if st.button("🔬 Run ADF Test"):
                        adf = analytics.adf_test(spread)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("P-Value", f"{adf['pvalue']:.4f}" if adf['pvalue'] else "N/A")
                        with col2:
                            is_stat = "✅ Stationary" if adf['is_stationary'] else "❌ Non-Stationary"
                            st.metric("Result", is_stat)
                else:
                    st.info("⏳ Collecting more data...")
            else:
                st.info("⏳ Waiting for data...")
        else:
            st.info("⏳ No data yet")

# Tab 3: Statistics
stats_tab = tab3 if len(symbols) == 2 else tab2

with stats_tab:
    st.subheader("📊 Statistical Analysis")
    
    for symbol in symbols:
        with st.expander(f"{symbol} Statistics", expanded=True):
            df = get_recent_data(symbol, limit=500)
            
            if not df.empty:
                stats = analytics.basic_statistics(df['price'])
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Mean", f"${stats['mean']:,.2f}")
                col2.metric("Std Dev", f"${stats['std']:,.2f}")
                col3.metric("Min", f"${stats['min']:,.2f}")
                col4.metric("Max", f"${stats['max']:,.2f}")
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {symbol} Data",
                    data=csv,
                    file_name=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("⏳ No data available")

# Tab 4: Alerts
alerts_tab = tab4 if len(symbols) == 2 else tab3

with alerts_tab:
    st.subheader("🚨 Alert System")
    
    # Custom alert creation
    with st.expander("➕ Create Custom Alert"):
        alert_name = st.text_input("Alert Name", "My Alert")
        alert_type = st.selectbox("Alert Type", ["Z-Score", "Price"])
        
        if alert_type == "Z-Score":
            threshold = st.number_input("Threshold", value=2.0, step=0.1)
            direction = st.radio("Direction", ["Above", "Below"])
            
            if st.button("Add Alert"):
                st.session_state.alert_manager.add_zscore_alert(
                    alert_name, threshold, above=(direction=="Above")
                )
                st.success(f"✅ Alert '{alert_name}' added!")
        else:
            symbol_alert = st.selectbox("Symbol", symbols)
            price_threshold = st.number_input("Price Threshold", value=50000.0, step=100.0)
            direction = st.radio("Direction", ["Above", "Below"])
            
            if st.button("Add Alert"):
                st.session_state.alert_manager.add_price_alert(
                    alert_name, symbol_alert, price_threshold, above=(direction=="Above")
                )
                st.success(f"✅ Alert '{alert_name}' added!")
    
    # Show active alerts
    st.subheader("📋 Active Alerts")
    active = st.session_state.alert_manager.get_active_alerts()
    
    if active:
        for alert in active:
            st.warning(f"🚨 **{alert.name}**: {alert.message}")
    else:
        st.info("✅ No active alerts")
    
    # Alert history
    st.subheader("📜 Alert History")
    history = st.session_state.alert_manager.get_alert_history()
    
    if history:
        for alert in reversed(history[-10:]):  # Show last 10
            st.text(f"{alert['time'].strftime('%H:%M:%S')} - {alert['message']}")
    else:
        st.info("No alerts triggered yet")

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()