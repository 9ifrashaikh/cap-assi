# Real-Time Crypto Analytics Dashboard

A complete analytical application for real-time cryptocurrency trading analysis, featuring live data ingestion from Binance, statistical analytics, pairs trading signals, and interactive visualization.

## 🎯 Overview

This application demonstrates end-to-end development capabilities for quantitative finance applications:
- **Backend**: Real-time WebSocket data ingestion, SQLite storage, multi-timeframe resampling
- **Analytics**: Statistical arbitrage metrics, cointegration tests, regression analysis
- **Frontend**: Interactive Streamlit dashboard with live charts and alerts

Built for traders and researchers at algorithmic trading firms focusing on statistical arbitrage, pairs trading, and quantitative analysis.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Internet connection (for Binance WebSocket)

### Installation

1. **Clone/Download the project:**
```bash
cd crypto-analytics
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Application

**Two terminals required:**

**Terminal 1 - Data Collection (WebSocket):**
```bash
python run_websocket.py
```
This continuously collects live tick data from Binance and stores it in SQLite. Leave it running in the background.

**Terminal 2 - Dashboard:**
```bash
python -m streamlit run app.py
```
Opens the interactive dashboard at `http://localhost:8501`

---

## 📁 Project Structure

```
crypto-analytics/
├── app.py                      # Main Streamlit dashboard
├── run_websocket.py            # Background WebSocket data collector
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── backend/
│   ├── database.py            # SQLite database operations
│   ├── websocket_client.py    # Binance WebSocket client
│   └── data_processor.py      # Data resampling & aggregation
│
├── analytics/
│   ├── statistics.py          # Core analytics (z-score, regression, ADF)
│   └── alerts.py              # Alert system for trading signals
│
├── data/
│   └── crypto_data.db         # SQLite database (auto-created)
│
└── tests/
    ├── test_day1.py           # Backend & data pipeline tests
    ├── test_day2.py           # Analytics & frontend tests
    └── final_test.py          # Comprehensive system test
```

---

## 🔧 Technical Architecture

### Data Flow

```
Binance API (WebSocket)
        ↓
WebSocket Client (backend/websocket_client.py)
        ↓
SQLite Database (data/crypto_data.db)
        ↓
Data Processor (resampling: 1s, 1m, 5m)
        ↓
Analytics Engine (statistics.py)
        ↓
Streamlit Dashboard (app.py)
```

### Key Design Decisions

**1. Database: SQLite**
- **Why**: Lightweight, zero-configuration, sufficient for single-day data requirements
- **Scalability**: Schema designed for easy migration to PostgreSQL/TimescaleDB
- **Indexing**: Composite index on (symbol, timestamp) for fast queries

**2. WebSocket Architecture**
- **Threading**: Separate thread for message processing to prevent blocking
- **Queue-based**: 1000-message buffer to handle high-frequency data
- **Error Handling**: Graceful degradation, automatic reconnection logic

**3. Data Resampling**
- **Method**: Pandas resampling with OHLCV aggregation
- **Timeframes**: 1s, 5s, 10s, 30s, 1min, 5min (user-selectable)
- **Performance**: In-memory processing with database persistence

**4. Frontend: Streamlit**
- **Why**: Rapid prototyping, built-in interactivity, minimal frontend code
- **Auto-refresh**: 2-second refresh rate for near-real-time updates
- **Scalability**: Design allows migration to Flask/FastAPI + React if needed

---

## 📊 Analytics Methodology

### 1. Pairs Trading Analysis

**Hedge Ratio Calculation (OLS Regression):**
```
Y = α + β*X + ε
```
Where:
- Y = Price of Asset 1 (e.g., BTC)
- X = Price of Asset 2 (e.g., ETH)
- β = Hedge ratio (how many units of X to hedge 1 unit of Y)

**Spread Calculation:**
```
Spread = Price_Asset1 - (Hedge_Ratio × Price_Asset2)
```

**Z-Score:**
```
Z = (Spread - Mean_Spread) / StdDev_Spread
```
Interpretation:
- Z > 2: Asset 1 overpriced relative to Asset 2 (potential sell signal)
- Z < -2: Asset 1 underpriced relative to Asset 2 (potential buy signal)

### 2. Stationarity Testing (ADF Test)

**Augmented Dickey-Fuller Test:**
- **Null Hypothesis**: Time series has a unit root (non-stationary)
- **P-value < 0.05**: Reject null → Series is stationary (mean-reverting)
- **Importance**: Pairs trading requires stationary spreads

### 3. Rolling Correlation

Measures time-varying correlation between two assets over a moving window.
- **Window**: User-configurable (default: 20 periods)
- **Range**: -1 (perfect negative) to +1 (perfect positive correlation)
- **Alert**: Triggers when correlation breaks down (e.g., < 0.5)

---

## 🚨 Alert System

### Built-in Alerts:
1. **Z-Score High** (threshold: +2.0)
2. **Z-Score Low** (threshold: -2.0)
3. **Z-Score Extreme High** (threshold: +3.0)
4. **Z-Score Extreme Low** (threshold: -3.0)

### Custom Alerts:
Users can create custom alerts via the dashboard:
- Price thresholds
- Correlation breakdowns
- Volume spikes
- Volatility changes

Alerts are displayed in real-time with priority levels (low/medium/high).

---

## 🧪 Testing

### Run Tests

**Backend & Data Pipeline:**
```bash
python test_day1.py
```
Tests: Database, WebSocket connection, data storage, resampling

**Analytics & Frontend:**
```bash
python test_day2.py
```
Tests: Statistical functions, alert system, regression models

**Comprehensive Test:**
```bash
python final_test.py
```
Tests everything and provides system readiness report.

### Expected Test Output
All tests should pass with:
- ✅ Database: Working
- ✅ WebSocket: Receiving ticks
- ✅ Analytics: Calculations correct
- ✅ Dashboard: Ready

---

## 📈 Features

### Current Features
- ✅ Live price charts (candlestick, configurable timeframes)
- ✅ Pairs trading analysis (hedge ratio, spread, z-score)
- ✅ Statistical tests (ADF test for cointegration)
- ✅ Rolling correlation analysis
- ✅ Customizable alert system
- ✅ CSV data export
- ✅ Multi-symbol support (BTC, ETH, BNB, SOL)
- ✅ Real-time updates (2-second refresh)

### Future Enhancements (Scalability Considerations)
- Kalman Filter for dynamic hedge ratio estimation
- Robust regression (Huber/Theil-Sen) for outlier resistance
- Mini backtesting engine with P&L tracking
- Order book data integration
- Multiple asset class support (equities, commodities, FX)
- REST API for external integrations
- Deployment to cloud (AWS/GCP) with Docker containerization

---

## 🛠️ Dependencies

Core libraries:
- **streamlit**: Dashboard framework
- **python-binance**: Binance API WebSocket client
- **pandas**: Data manipulation and time-series analysis
- **numpy**: Numerical computations
- **plotly**: Interactive charting
- **scipy**: Statistical tests
- **statsmodels**: Time-series econometrics (ADF test)
- **scikit-learn**: Regression models

See `requirements.txt` for complete list with versions.

---

## 📝 Development Notes

### Data Collection
- **Source**: Binance public WebSocket API (no authentication required)
- **Symbols**: BTCUSDT, ETHUSDT (configurable)
- **Frequency**: Real-time tick data (every trade)
- **Storage**: ~10-20 MB per hour of tick data

### Performance Considerations
- **Memory**: Keep last 10,000 ticks in memory for fast access
- **Database**: Indexed queries for sub-millisecond retrieval
- **Charts**: Limit to 500 most recent candles for smooth rendering
- **Refresh**: 2-second auto-refresh balances real-time feel with performance

### Known Limitations
- No authentication (public data only)
- Single-day data focus (as per requirements)
- Local deployment only (no multi-user support)

---

## 🤝 Contributing

This is a demonstration project for a recruitment assignment. For production use, consider:
1. Authentication and user management
2. Production database (PostgreSQL + TimescaleDB)
3. Caching layer (Redis)
4. API rate limiting
5. Error monitoring (Sentry)
6. Load balancing for multiple users

---

## 📄 License

This project is created as part of a technical assessment for educational and demonstration purposes.

---

## 👤 Author

Created for Quant Developer position evaluation.

**Contact**: [ifra.shaikh22@vit.edu]
**Date**: December 2025

---

## 🙏 Acknowledgments

- Binance for providing public WebSocket API
- Streamlit for rapid dashboard development framework
- Python data science ecosystem (Pandas, NumPy, SciPy)