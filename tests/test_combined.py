import sys
import time
from pathlib import Path

# Add project root to python path so we can resolve package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from communication.websocket_server import WebSocketServer
from communication.serial_manager import SerialManager

def main():
    """
    Combined test script that runs the WebSocket server and opens the USB
    serial monitor at the same time in a single terminal. 
    This eliminates the need to open multiple terminals in VS Code.
    """
    print("==================================================")
    print("      Combined Server & Serial Monitor Test")
    print("==================================================")
    
    # 1. Start the WebSocket server in the background
    server = WebSocketServer()
    server.start()
    
    # 2. Open the USB Serial connection to monitor ESP32 boot logs
    serial_monitor = SerialManager()
    if not serial_monitor.connect():
        print("[FAIL] Could not open USB serial port (COM9) for monitoring.")
        server.stop()
        sys.exit(1)
        
    print("\n[SUCCESS] WebSocket Server running & Serial Monitor active!")
    print("--------------------------------------------------")
    print("👉 Action: Press the physical EN/RST button on your ESP32 board now!")
    print("--------------------------------------------------\n")
    
    try:
        connected_test_triggered = False
        
        while True:
            # Read and print any logs coming from the ESP32 over USB Serial
            line = serial_monitor.read_line()
            if line:
                print(f"[ESP32 Serial] {line}")
                
            # Once we detect the ESP32 has connected to the WebSocket server:
            if server.is_connected and not connected_test_triggered:
                print("\n[WS SERVER] Wireless connection detected from ESP32!")
                time.sleep(1.0)
                
                # Transmit test speech payload over Wi-Fi
                test_phrase = "Websocket connection successful"
                print(f"[WS SERVER] Transmitting speech command: '{test_phrase}'")
                server.send_speech(test_phrase)
                
                connected_test_triggered = True
                print("[WS SERVER] Message sent! Listen to your speaker.")
                print("Continuing to monitor serial logs (press Ctrl+C to exit)...\n")
                
            # Reset the trigger if the client disconnects so we can test re-connection
            if not server.is_connected and connected_test_triggered:
                connected_test_triggered = False
                print("\n[WS SERVER] ESP32 disconnected. Waiting for reconnection...\n")

            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nStopping combined test...")
    finally:
        # Clean shutdown of both interfaces
        serial_monitor.close()
        server.stop()

if __name__ == "__main__":
    main()
