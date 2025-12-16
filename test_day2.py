"""
DAY 2 COMPLETE TEST
Tests analytics and alert system
"""
import pandas as pd
import numpy as np
from datetime import datetime

from analytics.statistics import TradingAnalytics
from analytics.alerts import AlertManager, create_default_alerts

def test_analytics():
    """Test analytics functions"""
    print("\n" + "=" * 60)
    print("TEST 1: Analytics Module")
    print("=" * 60)
    
    # Create sample data
    np.random.seed(42)
    n = 100
    series1 = pd.Series(100 + np.cumsum(np.random.randn(n) * 0.5))
    series2 = pd.Series(50 + np.cumsum(np.random.randn(n) * 0.3))
    
    analytics = TradingAnalytics()
    
    # Test 1: Hedge Ratio
    print("\n📊 Testing Hedge Ratio...")
    hedge = analytics.calculate_hedge_ratio(series1, series2)
    print(f"   Hedge Ratio: {hedge['hedge_ratio']:.4f}")
    print(f"   R²: {hedge['r_squared']:.4f}")
    
    if hedge['hedge_ratio'] != 0 and hedge['r_squared'] > 0:
        print("   ✅ Hedge ratio calculated")
    else:
        print("   ❌ Hedge ratio failed")
        return False
    
    # Test 2: Spread & Z-Score
    print("\n📊 Testing Spread & Z-Score...")
    spread = analytics.calculate_spread(series1, series2, hedge['hedge_ratio'])
    zscore = analytics.calculate_zscore(spread, window=20)
    
    if not spread.empty and not zscore.empty:
        print(f"   Spread mean: {spread.mean():.2f}")
        print(f"   Z-score current: {zscore.iloc[-1]:.2f}")
        print("   ✅ Spread and Z-score calculated")
    else:
        print("   ❌ Spread/Z-score failed")
        return False
    
    # Test 3: ADF Test
    print("\n📊 Testing ADF Test...")
    adf = analytics.adf_test(spread)
    
    if adf['pvalue'] is not None:
        print(f"   P-value: {adf['pvalue']:.4f}")
        print(f"   Is Stationary: {adf['is_stationary']}")
        print("   ✅ ADF test completed")
    else:
        print("   ❌ ADF test failed")
        return False
    
    # Test 4: Rolling Correlation
    print("\n📊 Testing Rolling Correlation...")
    corr = analytics.rolling_correlation(series1, series2, window=20)
    
    if not corr.empty:
        print(f"   Current correlation: {corr.iloc[-1]:.4f}")
        print("   ✅ Correlation calculated")
    else:
        print("   ❌ Correlation failed")
        return False
    
    # Test 5: Basic Statistics
    print("\n📊 Testing Basic Statistics...")
    stats = analytics.basic_statistics(series1)
    
    if stats and 'mean' in stats:
        print(f"   Mean: {stats['mean']:.2f}")
        print(f"   Std: {stats['std']:.2f}")
        print("   ✅ Statistics calculated")
    else:
        print("   ❌ Statistics failed")
        return False
    
    print("\n✅ Analytics test PASSED")
    return True


def test_alerts():
    """Test alert system"""
    print("\n" + "=" * 60)
    print("TEST 2: Alert System")
    print("=" * 60)
    
    # Create manager
    manager = create_default_alerts()
    
    print(f"\n📊 Created {len(manager.alerts)} default alerts")
    
    # Test data
    test_cases = [
        {'name': 'Normal', 'data': {'zscore': 1.0}, 'should_trigger': False},
        {'name': 'High Z-Score', 'data': {'zscore': 2.5}, 'should_trigger': True},
        {'name': 'Low Z-Score', 'data': {'zscore': -2.5}, 'should_trigger': True},
        {'name': 'Back to normal', 'data': {'zscore': 0.5}, 'should_trigger': False},
    ]
    
    print("\n📊 Testing alert triggers:\n")
    
    all_passed = True
    
    for test in test_cases:
        triggered = manager.check_all(test['data'])
        has_alert = len(triggered) > 0
        
        if has_alert == test['should_trigger']:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} {test['name']} (z={test['data']['zscore']:.1f}): "
              f"Expected alert: {test['should_trigger']}, Got: {has_alert}")
        
        if triggered:
            for alert in triggered:
                print(f"     🚨 {alert['message']}")
    
    # Check alert history
    history = manager.get_alert_history()
    print(f"\n📊 Alert History: {len(history)} alerts recorded")
    
    if all_passed:
        print("\n✅ Alert test PASSED")
    else:
        print("\n❌ Alert test FAILED")
    
    return all_passed


def run_all_tests():
    """Run all Day 2 tests"""
    print("\n" + "=" * 60)
    print("🚀 DAY 2 COMPLETE TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Analytics
    try:
        result = test_analytics()
        results.append(('Analytics', result))
    except Exception as e:
        print(f"❌ Analytics test error: {e}")
        import traceback
        traceback.print_exc()
        results.append(('Analytics', False))
    
    # Test 2: Alerts
    try:
        result = test_alerts()
        results.append(('Alerts', result))
    except Exception as e:
        print(f"❌ Alert test error: {e}")
        import traceback
        traceback.print_exc()
        results.append(('Alerts', False))
    
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
        print("\n🎉 ALL TESTS PASSED! Day 2 is complete!")
        print("\nYou now have:")
        print("  ✅ Analytics (z-score, regression, ADF, correlation)")
        print("  ✅ Alert system")
        print("  ✅ Streamlit dashboard")
        print("\n📝 Next: Run the dashboard!")
        print("\n🚀 To run:")
        print("   Terminal 1: python run_websocket.py")
        print("   Terminal 2: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()