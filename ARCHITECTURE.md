# System Architecture

## Data Flow Diagram
```
┌─────────────────────────────────────┐
│     Binance WebSocket API           │
│  (Real-time BTC/ETH Trade Stream)   │
└──────────────┬──────────────────────┘
               │ Live Ticks
               ▼
┌──────────────────────────────────────┐
│   WebSocket Client (Threading)       │
│  - Handles incoming messages         │
│  - Queue-based processing            │
└──────────────┬───────────────────────┘
               │ Tick Data
               ▼
┌──────────────────────────────────────┐
│      Database Handler                │
│  - save_tick()                       │
│  - get_recent_data()                 │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      SQLite Database                 │
│  Table: raw_ticks                    │
│  - timestamp, symbol, price, qty     │
│  - Indexed on (symbol, timestamp)    │
└──────────────┬───────────────────────┘
               │ Query
               ▼
┌──────────────────────────────────────┐
│      Data Processor                  │
│  - Resample to OHLCV                 │
│  - Timeframes: 1s, 1m, 5m            │
└──┬───────────────────────────────┬───┘
   │                               │
   ▼                               ▼
┌─────────────┐          ┌──────────────────┐
│  Resampled  │          │  Basic Stats     │
│  OHLCV Data │          │  (mean/std/etc)  │
└──────┬──────┘          └────────┬─────────┘
       │                          │
       └────────┬─────────────────┘
                ▼
┌──────────────────────────────────────┐
│      Analytics Engine                │
│  - calculate_hedge_ratio()           │
│  - calculate_spread()                │
│  - calculate_zscore()                │
│  - adf_test()                        │
│  - rolling_correlation()             │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      Alert Manager                   │
│  - Check conditions                  │
│  - Trigger alerts                    │
│  - Store history                     │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Streamlit Dashboard (Frontend)     │
│  ┌────────────────────────────────┐  │
│  │  Price Charts Tab              │  │
│  │  - Candlestick charts          │  │
│  │  - Multiple symbols            │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Spread Analysis Tab           │  │
│  │  - Hedge ratio display         │  │
│  │  - Spread chart                │  │
│  │  - Z-score with thresholds     │  │
│  │  - ADF test button             │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Statistics Tab                │  │
│  │  - Summary stats               │  │
│  │  - CSV export                  │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Alerts Tab                    │  │
│  │  - Active alerts               │  │
│  │  - Custom alert creation       │  │
│  │  - Alert history               │  │
│  └────────────────────────────────┘  │
└──────────────┬───────────────────────┘
               │ Auto-refresh (2s)
               ▼
┌──────────────────────────────────────┐
│         User Browser                 │
│    http://localhost:8501             │
└──────────────────────────────────────┘
```

## Component Interactions

1. **Data Ingestion**: WebSocket → Queue → Database (asynchronous, non-blocking)
2. **Data Processing**: Database → Processor → OHLCV (on-demand, cached)
3. **Analytics**: OHLCV → Analytics Engine → Results (computed per refresh)
4. **Visualization**: Results → Streamlit → Browser (2-second refresh cycle)
5. **Alerts**: Analytics → Alert Manager → Dashboard (real-time notifications)