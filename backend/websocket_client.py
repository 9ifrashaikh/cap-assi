"""
WebSocket client for connecting to Binance and streaming live tick data
"""
from binance import ThreadedWebsocketManager
import time
from datetime import datetime
import threading
import queue

class BinanceWebSocketClient:
    """
    Manages WebSocket connection to Binance for real-time trade data
    """
    
    def __init__(self, symbols=None):
        """
        Initialize WebSocket client
        
        Args:
            symbols (list): List of symbols to track (e.g., ['btcusdt', 'ethusdt'])
        """
        self.symbols = symbols or ['btcusdt']
        self.twm = None
        self.callbacks = []
        self.is_running = False
        self.tick_count = 0
        self.last_tick_time = None
        self.message_queue = queue.Queue(maxsize=1000)  # Larger queue
        self.processing_thread = None
        
    def add_callback(self, callback):
        """
        Add a callback function to be called when new data arrives
        
        Args:
            callback (function): Function that takes tick_data dict as argument
        """
        self.callbacks.append(callback)
    
    def _process_queue(self):
        """
        Process messages from queue in separate thread to prevent blocking
        """
        while self.is_running:
            try:
                # Get message with timeout to allow checking is_running
                msg = self.message_queue.get(timeout=0.1)  # Faster timeout
                self._process_message(msg)
                self.message_queue.task_done()  # Mark as processed
            except queue.Empty:
                continue
            except Exception as e:
                if self.is_running:  # Only log if we're supposed to be running
                    print(f"⚠️  Error processing message: {e}")
    
    def _handle_message(self, msg):
        """
        Internal message handler - just adds to queue
        
        Args:
            msg (dict): Message from Binance WebSocket
        """
        try:
            # Add to queue for processing
            if not self.message_queue.full():
                self.message_queue.put_nowait(msg)
            else:
                # Queue is full, skip this message (prevents crash)
                pass
        except Exception as e:
            pass  # Silently skip if queue operations fail
    
    def _process_message(self, msg):
        """
        Process a single message from the queue
        
        Args:
            msg (dict): Message from Binance WebSocket
        """
        try:
            # Check if it's a trade message
            if msg.get('e') == 'trade':
                tick_data = {
                    'timestamp': msg['T'],  # Trade time
                    'symbol': msg['s'],     # Symbol (e.g., BTCUSDT)
                    'price': float(msg['p']),  # Price
                    'quantity': float(msg['q'])  # Quantity
                }
                
                # Update stats
                self.tick_count += 1
                self.last_tick_time = datetime.now()
                
                # Call all registered callbacks
                for callback in self.callbacks:
                    try:
                        callback(tick_data)
                    except Exception as e:
                        print(f"❌ Error in callback: {e}")
                        
        except Exception as e:
            if self.is_running:
                print(f"❌ Error processing message: {e}")
    
    def start(self):
        """
        Start WebSocket connection and begin streaming data
        """
        if self.is_running:
            print("⚠️  WebSocket is already running")
            return
        
        try:
            print(f"🚀 Starting WebSocket for symbols: {self.symbols}")
            
            # Initialize ThreadedWebsocketManager with custom settings
            self.twm = ThreadedWebsocketManager()
            self.twm.start()
            
            # Give it a moment to initialize
            time.sleep(0.5)
            
            # Start processing thread
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.processing_thread.start()
            
            # Start trade socket for each symbol
            for symbol in self.symbols:
                self.twm.start_trade_socket(
                    callback=self._handle_message,
                    symbol=symbol.lower()
                )
                print(f"✅ Connected to {symbol.upper()}")
                time.sleep(0.2)  # Small delay between connections
            
            print("✅ WebSocket client started successfully")
            
        except Exception as e:
            print(f"❌ Error starting WebSocket: {e}")
            self.is_running = False
    
    def stop(self):
        """
        Stop WebSocket connection gracefully
        """
        if not self.is_running:
            return
        
        print("🛑 Stopping WebSocket client...")
        self.is_running = False
        
        try:
            # Give processing thread time to finish queue
            time.sleep(0.5)
            
            # Stop the websocket manager
            if self.twm:
                try:
                    self.twm.stop()
                except:
                    pass  # Suppress shutdown errors
            
            # Wait for processing thread to finish
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2)
            
            print("✅ WebSocket client stopped cleanly")
            
        except Exception as e:
            pass  # Suppress all shutdown errors
    
    def get_stats(self):
        """
        Get WebSocket connection statistics
        
        Returns:
            dict: Statistics including tick count, last tick time, etc.
        """
        return {
            'is_running': self.is_running,
            'tick_count': self.tick_count,
            'last_tick_time': self.last_tick_time,
            'symbols': self.symbols,
            'queue_size': self.message_queue.qsize()
        }


def simple_callback(tick_data):
    """
    Simple callback function for testing - prints only some data to avoid slowdown
    
    Args:
        tick_data (dict): Tick data from WebSocket
    """
    # Only print every 10th tick to avoid console slowdown
    import random
    if random.random() < 0.1:  # 10% chance to print
        print(f"📊 {tick_data['symbol']}: ${tick_data['price']:,.2f} | Qty: {tick_data['quantity']:.4f}")


if __name__ == "__main__":
    """
    Test the WebSocket client - run this to verify connection works
    """
    print("=" * 60)
    print("Testing Binance WebSocket Client")
    print("=" * 60)
    
    # Create client for BTC and ETH
    client = BinanceWebSocketClient(symbols=['btcusdt', 'ethusdt'])
    
    # Add a simple callback to print data
    client.add_callback(simple_callback)
    
    # Start the client
    client.start()
    
    print("\n⏳ Streaming live data for 30 seconds...\n")
    
    try:
        # Run for 30 seconds
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    
    finally:
        # Stop the client
        client.stop()
        
        # Show stats
        stats = client.get_stats()
        print("\n" + "=" * 60)
        print("📊 Session Statistics:")
        print(f"   Total ticks received: {stats['tick_count']}")
        print(f"   Last tick at: {stats['last_tick_time']}")
        print(f"   Queue size at end: {stats['queue_size']}")
        print("=" * 60)