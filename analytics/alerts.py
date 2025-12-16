"""
Alert system for trading signals
"""
from datetime import datetime
from typing import List, Dict, Callable

class Alert:
    """Single alert definition"""
    
    def __init__(self, name, condition, message, priority='medium'):
        """
        Create an alert
        
        Args:
            name (str): Alert name
            condition (callable): Function that returns True when alert triggers
            message (str): Alert message
            priority (str): 'low', 'medium', 'high'
        """
        self.name = name
        self.condition = condition
        self.message = message
        self.priority = priority
        self.triggered_at = None
        self.is_active = False
    
    def check(self, data):
        """
        Check if alert should trigger
        
        Args:
            data (dict): Data to check against
        
        Returns:
            bool: True if alert triggered
        """
        try:
            if self.condition(data):
                if not self.is_active:
                    self.is_active = True
                    self.triggered_at = datetime.now()
                return True
            else:
                self.is_active = False
            return False
        except Exception as e:
            print(f"❌ Error checking alert {self.name}: {e}")
            return False


class AlertManager:
    """Manages multiple alerts"""
    
    def __init__(self):
        self.alerts = []
        self.alert_history = []
    
    def add_alert(self, alert: Alert):
        """Add an alert to the manager"""
        self.alerts.append(alert)
    
    def add_zscore_alert(self, name, threshold, above=True):
        """
        Add a z-score threshold alert
        
        Args:
            name (str): Alert name
            threshold (float): Z-score threshold
            above (bool): True for > threshold, False for < threshold
        """
        if above:
            condition = lambda data: data.get('zscore', 0) > threshold
            message = f"Z-score crossed above {threshold}"
        else:
            condition = lambda data: data.get('zscore', 0) < threshold
            message = f"Z-score crossed below {threshold}"
        
        alert = Alert(name, condition, message, priority='high')
        self.add_alert(alert)
    
    def add_price_alert(self, name, symbol, threshold, above=True):
        """
        Add a price threshold alert
        
        Args:
            name (str): Alert name
            symbol (str): Trading symbol
            threshold (float): Price threshold
            above (bool): True for > threshold, False for < threshold
        """
        if above:
            condition = lambda data: data.get(f'price_{symbol}', 0) > threshold
            message = f"{symbol} price above ${threshold:,.2f}"
        else:
            condition = lambda data: data.get(f'price_{symbol}', 0) < threshold
            message = f"{symbol} price below ${threshold:,.2f}"
        
        alert = Alert(name, condition, message, priority='medium')
        self.add_alert(alert)
    
    def add_correlation_alert(self, name, threshold, below=True):
        """
        Add a correlation alert
        
        Args:
            name (str): Alert name
            threshold (float): Correlation threshold
            below (bool): True for < threshold, False for > threshold
        """
        if below:
            condition = lambda data: data.get('correlation', 1) < threshold
            message = f"Correlation dropped below {threshold}"
        else:
            condition = lambda data: data.get('correlation', 0) > threshold
            message = f"Correlation rose above {threshold}"
        
        alert = Alert(name, condition, message, priority='medium')
        self.add_alert(alert)
    
    def check_all(self, data):
        """
        Check all alerts
        
        Args:
            data (dict): Current data
        
        Returns:
            list: List of triggered alerts
        """
        triggered = []
        
        for alert in self.alerts:
            if alert.check(data):
                triggered.append({
                    'name': alert.name,
                    'message': alert.message,
                    'priority': alert.priority,
                    'time': alert.triggered_at
                })
                
                # Add to history if newly triggered
                if len(self.alert_history) == 0 or self.alert_history[-1]['name'] != alert.name:
                    self.alert_history.append({
                        'name': alert.name,
                        'message': alert.message,
                        'priority': alert.priority,
                        'time': alert.triggered_at
                    })
        
        return triggered
    
    def get_active_alerts(self):
        """Get all currently active alerts"""
        return [a for a in self.alerts if a.is_active]
    
    def get_alert_history(self, limit=50):
        """Get alert history"""
        return self.alert_history[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
        self.alert_history = []
    
    def remove_alert(self, name):
        """Remove an alert by name"""
        self.alerts = [a for a in self.alerts if a.name != name]


# Predefined alert templates
def create_default_alerts():
    """Create a set of default trading alerts"""
    manager = AlertManager()
    
    # Z-score alerts
    manager.add_zscore_alert("Z-Score High", threshold=2.0, above=True)
    manager.add_zscore_alert("Z-Score Low", threshold=-2.0, above=False)
    manager.add_zscore_alert("Z-Score Extreme High", threshold=3.0, above=True)
    manager.add_zscore_alert("Z-Score Extreme Low", threshold=-3.0, above=False)
    
    return manager


if __name__ == "__main__":
    """Test alert system"""
    print("=" * 60)
    print("Testing Alert System")
    print("=" * 60)
    
    # Create alert manager
    manager = create_default_alerts()
    
    # Test with different z-score values
    test_data = [
        {'zscore': 1.5, 'price_BTCUSDT': 50000},
        {'zscore': 2.5, 'price_BTCUSDT': 51000},
        {'zscore': 1.0, 'price_BTCUSDT': 49000},
        {'zscore': -2.5, 'price_BTCUSDT': 48000},
        {'zscore': 0.0, 'price_BTCUSDT': 50000},
    ]
    
    print("\n📊 Testing alerts with sample data:\n")
    
    for i, data in enumerate(test_data):
        print(f"Test {i+1}: Z-score = {data['zscore']:.1f}")
        triggered = manager.check_all(data)
        
        if triggered:
            for alert in triggered:
                print(f"  🚨 ALERT: {alert['message']}")
        else:
            print(f"  ✅ No alerts")
    
    print(f"\n📊 Alert History ({len(manager.get_alert_history())} total):")
    for alert in manager.get_alert_history():
        print(f"  - {alert['time'].strftime('%H:%M:%S')}: {alert['message']}")
    
    print("\n✅ Alert system test complete!")