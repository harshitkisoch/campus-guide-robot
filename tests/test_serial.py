import sys
import time
from pathlib import Path

# Add project root to python path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from communication.serial_manager import SerialManager

def run_serial_integration_test() -> None:
    """
    Connects to the ESP32 over serial, verifies connection, 
    sends a test message, and asserts the loopback response matches.
    """
    print("=== Testing ESP32 Serial Communication ===")
    
    # 1. Instantiate the Serial Manager
    manager = SerialManager()
    
    # 2. Attempt to open connection
    if not manager.connect():
        print("[FAIL] Could not establish connection to the COM port.")
        print("Please check your .env file and ensure the ESP32 is plugged in.")
        sys.exit(1)
        
    try:
        print("[INFO] Waiting for ESP32 boot signal...")
        boot_signal_found = False
        
        # We read a few lines to check for "ESP32 READY" in case of garbage boot characters
        start_wait = time.time()
        while time.time() - start_wait < 5.0:  # Timeout after 5 seconds
            line = manager.read_line()
            if line:
                print(f"[ESP32 Output] {line}")
            if "ESP32 READY" in line:
                boot_signal_found = True
                print("[INFO] Received READY signal from ESP32.")
                break
            time.sleep(0.1)
            
        if not boot_signal_found:
            print("[WARNING] Did not receive 'ESP32 READY' boot signal.")
            print("[WARNING] We will proceed with sending the message anyway...")

        # 3. Transmit the command
        test_payload = "Hello ESP32"
        print(f"[INFO] Sending: '{test_payload}'")
        if not manager.write_message(test_payload):
            print("[FAIL] Failed to write payload over serial.")
            sys.exit(1)
            
        # 4. Wait and read the response
        print("[INFO] Waiting for response...")
        time.sleep(0.5) # Brief pause for ESP32 processing
        
        response = manager.read_line()
        print(f"[ESP32 Output] {response}")
        
        # 5. Assert loopback verification
        expected_response = f"Received: {test_payload}"
        if response == expected_response:
            print("\n" + "=" * 30)
            print("         SUCCESS!         ")
            print("=" * 30 + "\n")
            print("[OK] ESP32 correctly received and echoed the message.")
        else:
            print(f"\n[FAIL] Response mismatch.")
            print(f"       Expected: '{expected_response}'")
            print(f"       Got:      '{response}'")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    finally:
        # 6. Ensure resource is released
        manager.close()

if __name__ == "__main__":
    run_serial_integration_test()
