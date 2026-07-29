import sys
import time
from pathlib import Path

# Add project root to python path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from communication.serial_manager import SerialManager

def test_esp32_audio_output() -> None:
    """
    Diagnostic script to send a test phrase to the ESP32
    to verify hardware DAC and HW-104 speaker output.
    """
    print("=== Testing ESP32 Speaker Speech Output ===")
    
    # 1. Initialize serial manager
    manager = SerialManager()
    
    # 2. Establish connection
    if not manager.connect():
        print("[FAIL] Could not connect to the ESP32 COM port.")
        sys.exit(1)
        
    try:
        print("[INFO] Waiting for ESP32 READY signal...")
        time.sleep(1.0) # Wait for hardware reset sequence to clear
        
        # 3. Transmit the test speech payload
        test_phrase = "Robot voice online"
        print(f"[INFO] Transmitting speech command: '{test_phrase}'")
        
        if not manager.write_message(test_phrase):
            print("[FAIL] Failed to transmit message.")
            sys.exit(1)
            
        print("[INFO] Message sent. Listen to your speaker!")
        print("Waiting to read loopback echo...")
        
        # 4. Check for echo back to confirm transmission succeeded
        response = manager.read_line()
        print(f"[ESP32 Echo] {response}")
        
        if f"Received: {test_phrase}" in response:
            print("\n[SUCCESS] ESP32 successfully received text and began speech synthesis!")
        else:
            print("\n[WARNING] Message was sent, but the loopback confirmation was different or timed out.")
            
    except KeyboardInterrupt:
        print("\nTest interrupted.")
    finally:
        manager.close()

if __name__ == "__main__":
    test_esp32_audio_output()
