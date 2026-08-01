import sys
import time
from pathlib import Path

# Add project root to python path so we can resolve package imports
sys.path.append(str(Path(__file__).resolve().parent))

from communication.websocket_server import WebSocketServer
from audio.audio_manager import AudioManager
from config.settings import settings

# Pre-defined showcase responses customized for JECRC University
PRESET_RESPONSES = {
    "1": ("Introduction", "Welcome freshers to J E C R C University, now the crazy builders of your college are coming and trust me you are not ready for this."),
    "2": ("Directions to Admissions", "The admissions block is located straight ahead, right next to the central library."),
    "3": ("Directions to Cafeteria", "You can find the cafeteria on the ground floor of the main engineering block."),
    "4": ("Robot Capabilities", "I am running on an E S P 32 controller, communicating wirelessly over WebSockets, with dual-mode audio support."),
    "5": ("Farewell", "Thank you for visiting our campus. Have a wonderful day!")
}

def run_automated_showcase(audio: AudioManager):
    """
    Plays the entire sequence of preset responses automatically with delays.
    """
    print("\n[DEMO] Starting Automated Showcase Sequence...")
    sequence = ["1", "2", "3", "4", "5"]
    
    for num in sequence:
        name, text = PRESET_RESPONSES[num]
        print(f"\n[DEMO] Speaking: [{name}] -> '{text}'")
        
        # Play via the audio abstraction layer
        audio.speak(text)
        
        # If the output device is the remote ESP32 speaker, we need to sleep 
        # to allow the physical audio on the board to finish playing.
        if settings.output_device.lower() == "esp32":
            duration = (len(text) * 0.08) + 2.5
            print(f"[DEMO] Waiting {duration:.1f} seconds for ESP32 speaker to finish...")
            time.sleep(duration)
        else:
            # Laptop SAPI5 audio is blocking, so just a brief transition pause
            time.sleep(1.0)
            
    print("\n[DEMO] Automated Showcase Sequence Complete!")

def main():
    print("==================================================")
    print("    CAMPUS GUIDE ROBOT - DUAL-MODE DEMO PANEL     ")
    print("==================================================")
    print(f"[INFO] Current Audio Output: [{settings.output_device.upper()}]")
    print("       (Change OUTPUT_DEVICE in .env to switch)")
    
    # 1. Initialize the WebSocket server
    server = WebSocketServer()
    server.start()
    
    # 2. Initialize the Audio Output Abstraction Layer (AudioManager)
    audio = AudioManager(server)
    
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
            print("\n[INFO] No ESP32 detected. Proceeding in Local Control Mode.")
        
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
                run_automated_showcase(audio)
                
            elif choice in PRESET_RESPONSES:
                label, text = PRESET_RESPONSES[choice]
                print(f"\n[DEMO] Activating: '{text}'")
                
                # Speak via the audio abstraction layer
                audio.speak(text)
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
