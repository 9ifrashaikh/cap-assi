"""
DAY 1 COMPLETE TEST
This script tests all Day 1 components together:
1. Database initialization
2. WebSocket connection
3. Data storage
4. Data retrieval
5. Resampling
"""

import time
import sys
from datetime import datetime

# Import our modules
from backend.database import init_database, save_tick, get_recent_data, get_tick_count, clear_database
from backend.websocket_client import BinanceWebSocketClient
from backend.data_processor import DataProcessor

def test_database():
    """Test 1: Database functions"""
    print("\n" + "=" * 60)
    print("TEST 1: Database Initialization and Operations")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Clear any existing data
    clear_database()
    
    # Test saving a tick
    test_tick = {
        'timestamp': int(datetime.now().timestamp() * 1000),
        'symbol': 'BTCUSDT',
        'price': 50000.0,
        'quantity': 0.1
    }
    
    print(f"\n📝 Saving test tick: {test_tick}")
    success = save_tick(test_tick)
    
    if success:
        print("✅ Tick saved successfully")
    else:
        print("❌ Failed to save tick")
        return False
    
    # Test retrieving data
    count = get_tick_count('BTCUSDT')
    print(f"📊 Ticks in database: {count}")
    
    if count > 0:
        print("✅ Database test PASSED")
        return True
    else:
        print("❌ Database test FAILED")
        return False


def test_full_pipeline():
    """Test 2: Complete pipeline - WebSocket → Database → Retrieval"""
    print("\n" + "=" * 60)
    print("TEST 2: Full Pipeline Integration Test")
    print("=" * 60)
    
    # Clear database
    clear_database()
    
    # Create WebSocket client
    client = BinanceWebSocketClient(symbols=['btcusdt', 'ethusdt'])
    
    # Counter for progress display
    tick_counter = {'count': 0}
    
    # Add callback to save to database and count
    def save_callback(tick_data):
        save_tick(tick_data)
        tick_counter['count'] += 1
        # Print every 50th tick
        if tick_counter['count'] % 50 == 0:
            print(f"   📊 {tick_counter['count']} ticks received...")
    
    client.add_callback(save_callback)
    
    print("\n🚀 Starting WebSocket and saving to database...")
    client.start()
    
    # Give it 2 seconds to establish connection
    time.sleep(2)
    
    print("⏳ Collecting data for 30 seconds...\n")
    
    # Show progress every 5 seconds
    for i in range(6):
        time.sleep(5)
        btc_count = get_tick_count('BTCUSDT')
        eth_count = get_tick_count('ETHUSDT')
        print(f"   [{(i+1)*5}s] BTC ticks: {btc_count} | ETH ticks: {eth_count}")
    
    print("\n🛑 Stopping WebSocket...")
    client.stop()
    
    # Give it a moment to finish processing
    time.sleep(1)
    
    # Verify data saved
    btc_count = get_tick_count('BTCUSDT')
    eth_count = get_tick_count('ETHUSDT')
    
    print(f"\n📊 Final counts - BTC: {btc_count} | ETH: {eth_count}")
    
    if btc_count > 0 and eth_count > 0:
        print("✅ Full pipeline test PASSED")
        
        # Test data retrieval
        print("\n📈 Testing data retrieval...")
        df = get_recent_data('BTCUSDT', limit=10)
        print(f"Retrieved {len(df)} records:")
        if not df.empty:
            print(df[['datetime', 'price', 'quantity']].head())
        
        return True
    else:
        print("❌ Full pipeline test FAILED")
        return False


def test_resampling():
    """Test 3: Data resampling"""
    print("\n" + "=" * 60)
    print("TEST 3: Data Resampling Test")
    print("=" * 60)
    
    # Get recent data
    df = get_recent_data('BTCUSDT', limit=1000)
    
    if df.empty:
        print("⚠️  No data available for resampling test")
        print("   Run Test 2 first to collect data")
        return False
    
    print(f"\n📊 Loaded {len(df)} ticks from database")
    
    # Create processor
    processor = DataProcessor()
    
    # Test different timeframes
    timeframes = [
        ('1s', '1 second'),
        ('5s', '5 seconds'),
        ('1min', '1 minute')
    ]
    
    success = True
    
    for tf_code, tf_name in timeframes:
        ohlcv = processor.resample_dataframe(df, tf_code)
        print(f"\n📊 Resampled to {tf_name}:")
        print(f"   Generated {len(ohlcv)} candles")
        if not ohlcv.empty:
            print(f"   Latest candle:")
            latest = ohlcv.iloc[-1]
            print(f"      Open:  ${latest['open']:,.2f}")
            print(f"      High:  ${latest['high']:,.2f}")
            print(f"      Low:   ${latest['low']:,.2f}")
            print(f"      Close: ${latest['close']:,.2f}")
            print(f"      Volume: {latest['volume']:.4f}")
        else:
            print(f"   ⚠️  No data for {tf_name}")
            success = False
    
    if success:
        print("\n✅ Resampling test PASSED")
    else:
        print("\n⚠️  Resampling test partially passed")
    
    return success


def run_all_tests():
    """Run all Day 1 tests"""
    print("\n" + "=" * 60)
    print("🚀 DAY 1 COMPLETE TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Database
    try:
        result = test_database()
        results.append(('Database', result))
    except Exception as e:
        print(f"❌ Database test error: {e}")
        results.append(('Database', False))
    
    # Test 2: Full pipeline (includes WebSocket test)
    try:
        result = test_full_pipeline()
        results.append(('WebSocket + Database', result))
    except Exception as e:
        print(f"❌ Full pipeline test error: {e}")
        import traceback
        traceback.print_exc()
        results.append(('WebSocket + Database', False))
    
    # Test 3: Resampling
    try:
        result = test_resampling()
        results.append(('Resampling', result))
    except Exception as e:
        print(f"❌ Resampling test error: {e}")
        results.append(('Resampling', False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Day 1 is complete!")
        print("\nYou now have:")
        print("  ✅ Working database")
        print("  ✅ Live WebSocket connection")
        print("  ✅ Data storage pipeline")
        print("  ✅ Data resampling")
        print("\n📝 Next: Move to Day 2 - Analytics & Frontend")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        if passed >= 2:
            print("\n💡 You have enough working to move forward!")
            print("   The core functionality (WebSocket + Database) is working.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    """
    Run this script to test all Day 1 components
    
    Usage:
        python test_day1.py
    """
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)