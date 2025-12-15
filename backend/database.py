"""
Database module for storing and retrieving tick data from Binance WebSocket
"""
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Database file path
DB_PATH = os.path.join('data', 'crypto_data.db')

def init_database():
    """
    Initialize the SQLite database and create tables if they don't exist
    """
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create raw ticks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp BIGINT NOT NULL,
            datetime TEXT NOT NULL,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
        ON raw_ticks(symbol, timestamp)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at: {DB_PATH}")


def save_tick(tick_data):
    """
    Save a single tick to the database
    
    Args:
        tick_data (dict): Dictionary containing timestamp, symbol, price, quantity
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Convert timestamp to datetime string
        dt = datetime.fromtimestamp(tick_data['timestamp'] / 1000.0)
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        cursor.execute('''
            INSERT INTO raw_ticks (timestamp, datetime, symbol, price, quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            tick_data['timestamp'],
            dt_str,
            tick_data['symbol'],
            tick_data['price'],
            tick_data['quantity']
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error saving tick: {e}")
        return False


def get_recent_data(symbol, limit=1000):
    """
    Get recent tick data for a symbol
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        limit (int): Number of recent records to fetch
    
    Returns:
        pandas.DataFrame: DataFrame with tick data
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        query = '''
            SELECT timestamp, datetime, symbol, price, quantity
            FROM raw_ticks
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(symbol, limit))
        conn.close()
        
        # Reverse to get chronological order
        df = df.iloc[::-1].reset_index(drop=True)
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()


def get_data_by_timerange(symbol, start_time, end_time=None):
    """
    Get tick data for a symbol within a time range
    
    Args:
        symbol (str): Trading pair symbol
        start_time (int): Start timestamp in milliseconds
        end_time (int): End timestamp in milliseconds (optional, defaults to now)
    
    Returns:
        pandas.DataFrame: DataFrame with tick data
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        if end_time is None:
            end_time = int(datetime.now().timestamp() * 1000)
        
        query = '''
            SELECT timestamp, datetime, symbol, price, quantity
            FROM raw_ticks
            WHERE symbol = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=(symbol, start_time, end_time))
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching time range data: {e}")
        return pd.DataFrame()


def get_tick_count(symbol=None):
    """
    Get count of ticks stored in database
    
    Args:
        symbol (str): Optional symbol filter
    
    Returns:
        int: Number of ticks
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('SELECT COUNT(*) FROM raw_ticks WHERE symbol = ?', (symbol,))
        else:
            cursor.execute('SELECT COUNT(*) FROM raw_ticks')
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
        
    except Exception as e:
        print(f"❌ Error getting tick count: {e}")
        return 0


def clear_database():
    """
    Clear all data from database (use for testing)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM raw_ticks')
        conn.commit()
        conn.close()
        print("✅ Database cleared")
        return True
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


if __name__ == "__main__":
    # Test the database functions
    print("Testing database module...")
    init_database()
    
    # Test saving a tick
    test_tick = {
        'timestamp': int(datetime.now().timestamp() * 1000),
        'symbol': 'BTCUSDT',
        'price': 50000.0,
        'quantity': 0.1
    }
    
    save_tick(test_tick)
    print(f"Ticks in database: {get_tick_count('BTCUSDT')}")