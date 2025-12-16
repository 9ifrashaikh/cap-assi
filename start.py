"""
Single-command startup script
Runs WebSocket and Dashboard together
"""
import subprocess
import sys
import time

print("🚀 Starting Crypto Analytics Dashboard")
print("=" * 60)

try:
    # Start WebSocket in background
    print("\n[1/2] Starting WebSocket data collection...")
    websocket_process = subprocess.Popen(
        [sys.executable, "run_websocket.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Give it time to start
    
    # Start Streamlit dashboard
    print("[2/2] Starting Streamlit dashboard...")
    print("\n✅ Dashboard will open in your browser!")
    print("📊 URL: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop both processes\n")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    
except KeyboardInterrupt:
    print("\n\n🛑 Stopping all processes...")
    websocket_process.terminate()
    print("✅ Stopped successfully")

except Exception as e:
    print(f"\n❌ Error: {e}")
    websocket_process.terminate()