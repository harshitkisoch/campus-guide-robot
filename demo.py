import sys
import time
from pathlib import Path

# Add project root to python path so we can resolve package imports
sys.path.append(str(Path(__file__).resolve().parent))

from communication.websocket_server import WebSocketServer
from audio.text_to_speech import TextToSpeech

# Pre-defined showcase responses customized for JECRC University
PRESET_RESPONSES = {
    "1": ("Introduction", "welcome to J E C R C University, now the crazy builders of your college are coming and trust me you are not ready for this"),
    "2": ("Directions to Admissions", "The admissions block is located straight ahead, right next to the central library."),
    "3": ("Directions to Cafeteria", "You can find the cafeteria on the ground floor of the main engineering block."),
    "4": ("Robot Capabilities", "I am running on an E S P 32 controller, communicating wirelessly over WebSockets, with audio playing via Bluetooth."),
    "5": ("Farewell", "Thank you for visiting our campus. Have a wonderful day!")
}

# Initialize local platform voice engine (SAPI5 on Windows)
tts = TextToSpeech()

def run_automated_showcase(server: WebSocketServer):
    """
    Plays the entire sequence of preset responses automatically with delays.
    Useful for a fully hands-free showcase.
    """
    print("\n[DEMO] Starting Automated Showcase Sequence...")
    sequence = ["1", "2", "3", "4", "5"]
    
    for num in sequence:
        name, text = PRESET_RESPONSES[num]
        print(f"\n[DEMO] Speaking: [{name}] -> '{text}'")
        
        # 1. Notify ESP32 over WebSocket
        if server.is_connected:
            server.send_message("status", {"action": "speaking", "text": text})
            
        # 2. Play speech locally on laptop (routes to paired Bluetooth speaker)
        tts.speak(text)
        
        # 3. Notify ESP32 speech is done
        if server.is_connected:
            server.send_message("status", {"action": "idle"})
            
        time.sleep(1.0) # Short break between sentences
            
    print("\n[DEMO] Automated Showcase Sequence Complete!")

def main():
    print("==================================================")
    print("    CAMPUS GUIDE ROBOT - EMERGENCY DEMO PANEL     ")
    print("==================================================")
    print("[INFO] This mode runs 100% offline (no Gemini API required).")
    print("[INFO] Audio plays through the laptop's default Bluetooth speaker.")
    
    # Initialize the WebSocket server
    server = WebSocketServer()
    server.start()
    
    print("\n[INFO] WebSocket server active. Please turn on your ESP32.")
    print("Waiting up to 3 seconds for wireless connection...")
    
    try:
        # Wait up to 3 seconds for the ESP32 to connect
        start_wait = time.time()
        while not server.is_connected and (time.time() - start_wait < 3.0):
            time.sleep(0.1)
            
        if server.is_connected:
            print("\n[SUCCESS] Robot connected wirelessly!")
            time.sleep(1.0)
        else:
            print("\n[INFO] No ESP32 detected. Running in Local Speaker Mode (Direct Bluetooth).")
        
        while True:
            print("\n--------------------------------------------------")
            print("                DEMO BOARD MENU                   ")
            print("--------------------------------------------------")
            for key, (label, text) in PRESET_RESPONSES.items():
                print(f" [{key}] Speak: {label}")
            print(" [A] Run FULL Automated Showcase (Intro to Farewell)")
            print(" [Q] Quit Demo")
            print("--------------------------------------------------")
            
            choice = input("Select an option: ").strip().upper()
            
            if choice == "Q":
                print("\nExiting Demo Panel. Goodbye!")
                break
                
            elif choice == "A":
                run_automated_showcase(server)
                
            elif choice in PRESET_RESPONSES:
                label, text = PRESET_RESPONSES[choice]
                print(f"\n[DEMO] Activating: '{text}'")
                
                # 1. Notify ESP32 speaking status
                if server.is_connected:
                    server.send_message("status", {"action": "speaking", "text": text})
                
                # 2. Speak locally (routes to Bluetooth speaker)
                tts.speak(text)
                
                # 3. Notify ESP32 idle status
                if server.is_connected:
                    server.send_message("status", {"action": "idle"})
                    
                print("[DEMO] Playback complete.")
                    
            else:
                print("\n[INVALID OPTION] Please choose a valid number or option.")
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
