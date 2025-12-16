"""
Real-Time Crypto Analytics Dashboard - ENHANCED VERSION
Includes: Volume analysis, OHLC upload, advanced features
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import io

# Import our modules
from backend.database import init_database, get_recent_data, get_tick_count, save_tick
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
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# Initialize database
init_database()

# Sidebar controls
st.sidebar.title("⚙️ Controls")

# OHLC Upload Feature
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Upload OHLC Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV (optional)", type=['csv'])

if uploaded_file is not None:
    try:
        df_upload = pd.read_csv(uploaded_file)
        st.session_state.uploaded_data = df_upload
        st.sidebar.success(f"✅ Loaded {len(df_upload)} rows")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")

st.sidebar.markdown("---")

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
st.markdown("*Professional-grade trading analytics with real-time data*")
st.markdown("---")

# Status bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    status = "🟢 LIVE" if st.session_state.websocket_started else "🔴 STOPPED"
    st.metric("Status", status)

with col2:
    total_ticks = sum([get_tick_count(sym) for sym in symbols])
    st.metric("Total Ticks", f"{total_ticks:,}")

with col3:
    if st.session_state.uploaded_data is not None:
        st.metric("Uploaded Rows", f"{len(st.session_state.uploaded_data):,}")
    else:
        st.metric("Uploaded Data", "None")

with col4:
    st.metric("Symbols", len(symbols))

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
    tabs = st.tabs(["📈 Price & Volume", "📊 Statistics", "🚨 Alerts"])
    tab1, tab2, tab3 = tabs
else:
    tabs = st.tabs(["📈 Price & Volume", "📊 Spread Analysis", "📉 Statistics", "🚨 Alerts"])
    tab1, tab2, tab3, tab4 = tabs

# Tab 1: Price & Volume Charts
with tab1:
    st.subheader("Live Price & Volume Analysis")
    
    for symbol in symbols:
        with st.expander(f"{symbol} - Click to expand", expanded=True):
            # Get data
            df = get_recent_data(symbol, limit=500)
            
            if not df.empty:
                # Resample to OHLCV
                ohlcv = processor.resample_dataframe(df, timeframe)
                
                if not ohlcv.empty:
                    # Create subplot with price and volume
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        subplot_titles=(f'{symbol} Price', 'Volume'),
                        row_heights=[0.7, 0.3]
                    )
                    
                    # Candlestick chart
                    fig.add_trace(
                        go.Candlestick(
                            x=ohlcv['datetime'],
                            open=ohlcv['open'],
                            high=ohlcv['high'],
                            low=ohlcv['low'],
                            close=ohlcv['close'],
                            name='Price'
                        ),
                        row=1, col=1
                    )
                    
                    # Volume bar chart
                    colors = ['red' if ohlcv['close'].iloc[i] < ohlcv['open'].iloc[i] 
                             else 'green' for i in range(len(ohlcv))]
                    
                    fig.add_trace(
                        go.Bar(
                            x=ohlcv['datetime'],
                            y=ohlcv['volume'],
                            name='Volume',
                            marker_color=colors
                        ),
                        row=2, col=1
                    )
                    
                    fig.update_layout(
                        height=600,
                        template="plotly_dark",
                        showlegend=False,
                        xaxis_rangeslider_visible=False
                    )
                    
                    fig.update_xaxes(title_text="Time", row=2, col=1)
                    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
                    fig.update_yaxes(title_text="Volume", row=2, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Current stats
                    col1, col2, col3, col4, col5 = st.columns(5)
                    current_price = ohlcv['close'].iloc[-1]
                    price_change = ((current_price - ohlcv['open'].iloc[0]) / ohlcv['open'].iloc[0]) * 100
                    avg_volume = ohlcv['volume'].mean()
                    total_trades = ohlcv['trade_count'].sum()
                    
                    col1.metric("Current", f"${current_price:,.2f}")
                    col2.metric("Change", f"{price_change:+.2f}%")
                    col3.metric("Avg Volume", f"{avg_volume:.4f}")
                    col4.metric("Trades", f"{int(total_trades):,}")
                    col5.metric("Ticks", get_tick_count(symbol))
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
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Hedge Ratio", f"{hedge['hedge_ratio']:.4f}")
                    col2.metric("R²", f"{hedge['r_squared']:.4f}")
                    if not zscore.empty:
                        current_z = zscore.iloc[-1]
                        col3.metric("Current Z-Score", f"{current_z:.2f}")
                        
                        # Trading signal
                        if current_z > 2:
                            signal = "🔴 SELL (Overvalued)"
                        elif current_z < -2:
                            signal = "🟢 BUY (Undervalued)"
                        else:
                            signal = "⚪ NEUTRAL"
                        col4.metric("Signal", signal)
                    
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
                        fig.add_hline(y=2, line_dash="dash", line_color="red", row=2, col=1, 
                                    annotation_text="Overbought")
                        fig.add_hline(y=-2, line_dash="dash", line_color="green", row=2, col=1,
                                    annotation_text="Oversold")
                        fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)
                    
                    fig.update_layout(height=600, template="plotly_dark", showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # ADF Test
                    st.markdown("---")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if st.button("🔬 Run ADF Stationarity Test", type="primary"):
                            with st.spinner("Running test..."):
                                adf = analytics.adf_test(spread)
                                
                                st.markdown("### Test Results")
                                st.metric("P-Value", f"{adf['pvalue']:.4f}" if adf['pvalue'] else "N/A")
                                st.metric("Test Statistic", f"{adf['statistic']:.4f}" if adf['statistic'] else "N/A")
                                
                                if adf['is_stationary']:
                                    st.success("✅ Spread is STATIONARY (good for pairs trading)")
                                else:
                                    st.warning("⚠️ Spread is NON-STATIONARY")
                    
                    with col2:
                        st.markdown("### What is ADF Test?")
                        st.info("""
                        **Augmented Dickey-Fuller Test** checks if the spread is mean-reverting (stationary).
                        
                        - **P-value < 0.05**: Spread is stationary ✅ (good for pairs trading)
                        - **P-value > 0.05**: Spread is non-stationary ❌ (risky for pairs trading)
                        
                        Stationary spreads tend to revert to their mean, making them suitable for statistical arbitrage.
                        """)
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
                
                col5, col6, col7, col8 = st.columns(4)
                col5.metric("Median", f"${stats['median']:,.2f}")
                col6.metric("Skewness", f"{stats['skew']:.3f}")
                col7.metric("Kurtosis", f"{stats['kurtosis']:.3f}")
                col8.metric("Count", f"{stats['count']:,}")
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {symbol} Data (CSV)",
                    data=csv,
                    file_name=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("⏳ No data available")

# Tab 4: Alerts
alerts_tab = tab4 if len(symbols) == 2 else tab3

with alerts_tab:
    st.subheader("🚨 Alert System")
    
    # Custom alert creation
    with st.expander("➕ Create Custom Alert", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            alert_name = st.text_input("Alert Name", "My Alert")
            alert_type = st.selectbox("Alert Type", ["Z-Score", "Price", "Correlation"])
        
        with col2:
            if alert_type == "Z-Score":
                threshold = st.number_input("Threshold", value=2.0, step=0.1)
                direction = st.radio("Direction", ["Above", "Below"], horizontal=True)
                
                if st.button("Add Alert", type="primary"):
                    st.session_state.alert_manager.add_zscore_alert(
                        alert_name, threshold, above=(direction=="Above")
                    )
                    st.success(f"✅ Alert '{alert_name}' added!")
                    
            elif alert_type == "Price":
                symbol_alert = st.selectbox("Symbol", symbols)
                price_threshold = st.number_input("Price Threshold", value=50000.0, step=100.0)
                direction = st.radio("Direction", ["Above", "Below"], horizontal=True)
                
                if st.button("Add Alert", type="primary"):
                    st.session_state.alert_manager.add_price_alert(
                        alert_name, symbol_alert, price_threshold, above=(direction=="Above")
                    )
                    st.success(f"✅ Alert '{alert_name}' added!")
                    
            else:  # Correlation
                corr_threshold = st.number_input("Correlation Threshold", value=0.5, step=0.05, 
                                                min_value=-1.0, max_value=1.0)
                direction = st.radio("Direction", ["Below", "Above"], horizontal=True)
                
                if st.button("Add Alert", type="primary"):
                    st.session_state.alert_manager.add_correlation_alert(
                        alert_name, corr_threshold, below=(direction=="Below")
                    )
                    st.success(f"✅ Alert '{alert_name}' added!")
    
    # Check alerts with current data
    if len(symbols) == 2:
        df1 = get_recent_data(symbols[0], limit=100)
        df2 = get_recent_data(symbols[1], limit=100)
        
        if not df1.empty and not df2.empty:
            ohlcv1 = processor.resample_dataframe(df1, timeframe)
            ohlcv2 = processor.resample_dataframe(df2, timeframe)
            
            if not ohlcv1.empty and not ohlcv2.empty:
                merged = pd.merge(ohlcv1[['datetime', 'close']], ohlcv2[['datetime', 'close']], 
                                on='datetime', suffixes=('_1', '_2'))
                
                if len(merged) > 2:
                    hedge = analytics.calculate_hedge_ratio(merged['close_1'], merged['close_2'])
                    spread = analytics.calculate_spread(merged['close_1'], merged['close_2'], hedge['hedge_ratio'])
                    zscore = analytics.calculate_zscore(spread, window=20)
                    
                    if not zscore.empty:
                        current_data = {
                            'zscore': zscore.iloc[-1],
                            f'price_{symbols[0]}': merged['close_1'].iloc[-1],
                            f'price_{symbols[1]}': merged['close_2'].iloc[-1],
                        }
                        
                        triggered = st.session_state.alert_manager.check_all(current_data)
    
    # Show active alerts
    st.markdown("---")
    st.subheader("📋 Active Alerts")
    active = st.session_state.alert_manager.get_active_alerts()
    
    if active:
        for alert in active:
            st.warning(f"🚨 **{alert.name}**: {alert.message}")
    else:
        st.success("✅ No active alerts")
    
    # Alert history
    st.markdown("---")
    st.subheader("📜 Alert History (Last 10)")
    history = st.session_state.alert_manager.get_alert_history()
    
    if history:
        for alert in reversed(history[-10:]):
            st.text(f"{alert['time'].strftime('%H:%M:%S')} - {alert['message']}")
    else:
        st.info("No alerts triggered yet")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Refresh rate: {refresh_rate}s")

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()