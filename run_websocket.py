"""
Background WebSocket runner - CLEAN VERSION
"""
import time
from datetime import datetime
from backend.database import init_database, save_tick, get_tick_count
from binance import ThreadedWebsocketManager

def main():
    print("🚀 BACKGROUND WEBSOCKET RUNNER")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    init_database()
    
    # Simple counter
    tick_count = {'count': 0, 'last_print': time.time()}
    
    def handle_tick(msg):
        if msg.get('e') == 'trade':
            tick_data = {
                'timestamp': msg['T'],
                'symbol': msg['s'],
                'price': float(msg['p']),
                'quantity': float(msg['q'])
            }
            save_tick(tick_data)
            tick_count['count'] += 1
            
            # Print every 10 seconds
            if time.time() - tick_count['last_print'] > 10:
                btc = get_tick_count('BTCUSDT')
                eth = get_tick_count('ETHUSDT')
                print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC: {btc:,} | ETH: {eth:,} | Rate: {tick_count['count']/10:.1f}/sec")
                tick_count['count'] = 0
                tick_count['last_print'] = time.time()
    
    # Start WebSocket
    twm = ThreadedWebsocketManager()
    twm.start()
    twm.start_trade_socket(callback=handle_tick, symbol='btcusdt')
    twm.start_trade_socket(callback=handle_tick, symbol='ethusdt')
    
    print("✅ WebSocket running! Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⚠️  Stopping...")
        try:
            twm.stop()
        except:
            pass
        
        btc = get_tick_count('BTCUSDT')
        eth = get_tick_count('ETHUSDT')
        print(f"\n📊 FINAL: BTC: {btc:,} | ETH: {eth:,} | Total: {btc+eth:,}")

if __name__ == "__main__":
    main()