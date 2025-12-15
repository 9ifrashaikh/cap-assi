"""
Data processor for resampling tick data into different timeframes (1s, 1m, 5m)
"""
import pandas as pd
from datetime import datetime, timedelta

class DataProcessor:
    """
    Processes raw tick data and resamples into OHLCV format
    """
    
    def __init__(self):
        self.tick_buffer = []
        self.max_buffer_size = 10000  # Keep last 10k ticks in memory
    
    def add_tick(self, tick_data):
        """
        Add a tick to the internal buffer
        
        Args:
            tick_data (dict): Tick data from WebSocket
        """
        self.tick_buffer.append(tick_data)
        
        # Keep buffer size manageable
        if len(self.tick_buffer) > self.max_buffer_size:
            self.tick_buffer = self.tick_buffer[-self.max_buffer_size:]
    
    def resample_dataframe(self, df, timeframe='1min'):
        """
        Resample tick data into OHLCV format
        
        Args:
            df (pd.DataFrame): DataFrame with columns: timestamp, price, quantity
            timeframe (str): Pandas timeframe string ('1s', '1min', '5min', etc.)
                            1s = 1 second, 1min = 1 minute, 5min = 5 minutes
        
        Returns:
            pd.DataFrame: Resampled OHLCV data
        """
        if df.empty:
            return pd.DataFrame()
        
        try:
            # Create a copy to avoid modifying original
            df = df.copy()
            
            # Convert timestamp to datetime
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            # Resample to OHLCV using proper aggregation
            resampled = df.resample(timeframe)
            
            ohlcv = pd.DataFrame({
                'open': resampled['price'].first(),
                'high': resampled['price'].max(),
                'low': resampled['price'].min(),
                'close': resampled['price'].last(),
                'volume': resampled['quantity'].sum(),
                'trade_count': resampled['price'].count()
            })
            
            # Remove NaN rows (periods with no trades)
            ohlcv = ohlcv.dropna()
            
            # Reset index to have datetime as column
            ohlcv = ohlcv.reset_index()
            
            return ohlcv
            
        except Exception as e:
            print(f"❌ Error resampling data: {e}")
            return pd.DataFrame()
    
    def resample_ticks(self, ticks, timeframe='1min'):
        """
        Resample list of ticks into OHLCV format
        
        Args:
            ticks (list): List of tick dictionaries
            timeframe (str): Timeframe for resampling
        
        Returns:
            pd.DataFrame: Resampled OHLCV data
        """
        if not ticks:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(ticks)
        
        # Resample
        return self.resample_dataframe(df, timeframe)
    
    def get_latest_ohlcv(self, df, timeframe='1min', periods=100):
        """
        Get latest OHLCV candles
        
        Args:
            df (pd.DataFrame): Raw tick data
            timeframe (str): Timeframe for resampling
            periods (int): Number of candles to return
        
        Returns:
            pd.DataFrame: Latest OHLCV candles
        """
        ohlcv = self.resample_dataframe(df, timeframe)
        
        if not ohlcv.empty:
            return ohlcv.tail(periods)
        
        return pd.DataFrame()
    
    def calculate_vwap(self, df):
        """
        Calculate Volume Weighted Average Price
        
        Args:
            df (pd.DataFrame): DataFrame with price and quantity columns
        
        Returns:
            float: VWAP value
        """
        if df.empty:
            return 0.0
        
        try:
            total_volume = df['quantity'].sum()
            if total_volume == 0:
                return df['price'].mean()
            
            vwap = (df['price'] * df['quantity']).sum() / total_volume
            return vwap
            
        except Exception as e:
            print(f"❌ Error calculating VWAP: {e}")
            return 0.0
    
    def get_tick_stats(self, ticks):
        """
        Calculate basic statistics from tick data
        
        Args:
            ticks (list): List of tick dictionaries
        
        Returns:
            dict: Statistics including min, max, mean, std, etc.
        """
        if not ticks:
            return {}
        
        try:
            df = pd.DataFrame(ticks)
            
            stats = {
                'count': len(df),
                'mean_price': df['price'].mean(),
                'std_price': df['price'].std(),
                'min_price': df['price'].min(),
                'max_price': df['price'].max(),
                'total_volume': df['quantity'].sum(),
                'vwap': self.calculate_vwap(df),
                'first_timestamp': df['timestamp'].iloc[0],
                'last_timestamp': df['timestamp'].iloc[-1]
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error calculating stats: {e}")
            return {}


if __name__ == "__main__":
    """
    Test the data processor
    """
    print("=" * 60)
    print("Testing Data Processor")
    print("=" * 60)
    
    # Create sample tick data
    import time
    base_time = int(time.time() * 1000)
    
    sample_ticks = []
    for i in range(100):
        tick = {
            'timestamp': base_time + (i * 1000),  # 1 tick per second
            'symbol': 'BTCUSDT',
            'price': 50000 + (i % 20) * 10,  # Price fluctuates
            'quantity': 0.1 + (i % 5) * 0.01
        }
        sample_ticks.append(tick)
    
    # Create processor
    processor = DataProcessor()
    
    # Test resampling to 1 minute
    print("\n📊 Resampling to 1-minute candles...")
    ohlcv_1m = processor.resample_ticks(sample_ticks, '1min')
    print(ohlcv_1m.head())
    
    # Test resampling to 5 seconds
    print("\n📊 Resampling to 5-second candles...")
    ohlcv_5s = processor.resample_ticks(sample_ticks, '5s')
    print(ohlcv_5s.head())
    
    # Test statistics
    print("\n📊 Tick Statistics:")
    stats = processor.get_tick_stats(sample_ticks)
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Data processor test complete!")