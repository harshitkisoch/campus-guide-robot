import sys
import time
from pathlib import Path

# Add project root to python path so we can resolve package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from communication.websocket_server import WebSocketServer

def main():
    """
    Test script that launches the Python WebSocket server and waits for the
    real ESP32 to connect wirelessly. Once connected, it transmits a test
    phrase to verify audio playback over the network.
    """
    print("==================================================")
    print("   ESP32 WebSocket Client Connection Test")
    print("==================================================")
    
    # 1. Start the server
    server = WebSocketServer()
    server.start()
    
    print("\n[INFO] WebSocket server is active. Please turn on/reset your ESP32.")
    print("Waiting for wireless connection...")
    
    try:
        # 2. Wait up to 60 seconds for the ESP32 to connect over Wi-Fi
        start_time = time.time()
        while time.time() - start_time < 60.0:
            if server.is_connected:
                print("\n[SUCCESS] Physical ESP32 connected over Wi-Fi!")
                time.sleep(1.5) # Give the connection a moment to settle
                
                # 3. Transmit a test speech payload
                test_phrase = "Websocket connection successful"
                print(f"[INFO] Transmitting test speech: '{test_phrase}'")
                
                if server.send_speech(test_phrase):
                    print("[INFO] Speech command delivered. Listen to your speaker!")
                else:
                    print("[FAIL] Failed to deliver speech command.")
                
                # 4. Monitor the connection for a short period to observe ACKs/Heartbeats
                print("Monitoring socket for 10 seconds...")
                time.sleep(10.0)
                break
            time.sleep(0.5)
        else:
            print("\n[TIMEOUT] No ESP32 connected within 60 seconds.")
            
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
