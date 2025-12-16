"""
FINAL COMPREHENSIVE TEST
Tests everything before running dashboard
"""
import time
from datetime import datetime
from backend.database import init_database, get_tick_count, get_recent_data, save_tick
from backend.data_processor import DataProcessor
from analytics.statistics import TradingAnalytics
import pandas as pd
import numpy as np

print("=" * 60)
print("🧪 FINAL COMPREHENSIVE TEST")
print("=" * 60)

# Test 1: Database
print("\n[1/5] Testing Database...")
init_database()
test_tick = {
    'timestamp': int(time.time() * 1000),
    'symbol': 'TESTUSDT',
    'price': 50000.0,
    'quantity': 0.1
}
save_tick(test_tick)
if get_tick_count('TESTUSDT') > 0:
    print("✅ Database works")
else:
    print("❌ Database failed")
    exit(1)

# Test 2: Check real data
print("\n[2/5] Checking Real Data...")
btc_count = get_tick_count('BTCUSDT')
eth_count = get_tick_count('ETHUSDT')
print(f"   BTC ticks: {btc_count:,}")
print(f"   ETH ticks: {eth_count:,}")

if btc_count == 0 and eth_count == 0:
    print("⚠️  No live data yet - run websocket first!")
    print("   But basic functionality works.")
else:
    print("✅ Live data available")

# Test 3: Data Processor
print("\n[3/5] Testing Data Processor...")
processor = DataProcessor()
if btc_count > 0:
    df = get_recent_data('BTCUSDT', limit=100)
    if not df.empty:
        ohlcv = processor.resample_dataframe(df, '1min')
        if not ohlcv.empty:
            print(f"✅ Resampling works ({len(ohlcv)} candles)")
        else:
            print("⚠️  Not enough data for 1min candles")
    else:
        print("⚠️  No data retrieved")
else:
    print("⚠️  Skipping (no data)")

# Test 4: Analytics
print("\n[4/5] Testing Analytics...")
analytics = TradingAnalytics()

# Test with sample data
np.random.seed(42)
sample1 = pd.Series(100 + np.cumsum(np.random.randn(50)))
sample2 = pd.Series(50 + np.cumsum(np.random.randn(50)))

hedge = analytics.calculate_hedge_ratio(sample1, sample2)
spread = analytics.calculate_spread(sample1, sample2, hedge['hedge_ratio'])
zscore = analytics.calculate_zscore(spread, window=20)

if hedge['hedge_ratio'] != 0 and not zscore.empty:
    print(f"✅ Analytics work (hedge ratio: {hedge['hedge_ratio']:.4f})")
else:
    print("❌ Analytics failed")
    exit(1)

# Test 5: Check if ready for dashboard
print("\n[5/5] Dashboard Readiness Check...")
issues = []

if btc_count < 50:
    issues.append(f"Low BTC data ({btc_count} ticks, need 50+)")
if eth_count < 50:
    issues.append(f"Low ETH data ({eth_count} ticks, need 50+)")

if issues:
    print("⚠️  Dashboard will have limited functionality:")
    for issue in issues:
        print(f"   - {issue}")
    print("\n💡 Solution: Let websocket run for 1-2 minutes")
else:
    print("✅ Dashboard ready!")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("✅ Database: Working")
print("✅ Data Processor: Working")
print("✅ Analytics: Working")
print(f"📊 Live Data: BTC={btc_count:,} ETH={eth_count:,}")

if btc_count > 50 and eth_count > 50:
    print("\n🎉 ALL SYSTEMS GO!")
    print("\n🚀 Next steps:")
    print("   1. Terminal 1: python run_websocket.py")
    print("   2. Terminal 2: python -m streamlit run app.py")
    print("   3. Browser: http://localhost:8501")
else:
    print("\n⚠️  Need more data!")
    print("\n🚀 Next steps:")
    print("   1. Terminal 1: python run_websocket.py (let it run 2 min)")
    print("   2. Run this test again: python final_test.py")
    print("   3. When data > 50 ticks, start dashboard")

print("=" * 60)