"""
Background WebSocket - WORKING VERSION
"""
import time
from datetime import datetime
from backend.database import init_database, save_tick, get_tick_count
from binance import ThreadedWebsocketManager

def main():
    print("🚀 Starting WebSocket Data Collection")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    init_database()
    
    tick_stats = {'count': 0, 'last_print': time.time()}
    
    def handle_message(msg):
        try:
            if msg.get('e') == 'trade':
                tick_data = {
                    'timestamp': msg['T'],
                    'symbol': msg['s'],
                    'price': float(msg['p']),
                    'quantity': float(msg['q'])
                }
                save_tick(tick_data)
                tick_stats['count'] += 1
                
                now = time.time()
                if now - tick_stats['last_print'] >= 10:
                    btc = get_tick_count('BTCUSDT')
                    eth = get_tick_count('ETHUSDT')
                    rate = tick_stats['count'] / 10
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"BTC: {btc:,} | ETH: {eth:,} | Rate: {rate:.1f}/sec")
                    tick_stats['count'] = 0
                    tick_stats['last_print'] = now
        except:
            pass
    
    twm = ThreadedWebsocketManager()
    twm.start()
    time.sleep(1)
    
    twm.start_trade_socket(callback=handle_message, symbol='btcusdt')
    twm.start_trade_socket(callback=handle_message, symbol='ethusdt')
    
    print("✅ WebSocket started!")
    print("📊 Collecting data (Ctrl+C to stop)\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        try:
            twm.stop()
        except:
            pass
        btc = get_tick_count('BTCUSDT')
        eth = get_tick_count('ETHUSDT')
        print(f"\n📊 Final: BTC={btc:,} ETH={eth:,}")

if __name__ == "__main__":
    main()