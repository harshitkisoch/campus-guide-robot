import time
import re
from brain.gemini_client import GeminiClient
from communication.websocket_server import WebSocketServer
from communication.web_server import RobotWebServer
from audio.audio_manager import AudioManager

class ConversationPipeline:
    """
    Orchestrates the entire AI conversation flow:
    Keyboard input -> Gemini Client API -> Decoupled Audio Layer.
    """
    def __init__(self) -> None:
        """
        Initializes core modules needed for the conversation.
        """
        print("[PIPELINE] Initializing core modules...")
        self.gemini = GeminiClient()
        
        # Initialize and start the HTTP Web Server (Port 8000)
        self.web_server = RobotWebServer()
        self.web_server.start()
        
        # Initialize and start the WebSocket Server (Port 8765)
        self.ws_server = WebSocketServer()
        self.ws_server.start()
        
        # Register incoming web query callback
        self.ws_server.on_query_callback = self.run_turn
        
        # Initialize the Decoupled Audio Layer (Factory Router)
        self.audio = AudioManager(self.ws_server)
        
        # Generate and print the permanent terminal QR Code for local connections
        from communication.qr_generator import generate_qr_code
        generate_qr_code()
            
        print("[PIPELINE] Ready.")

    def run_turn(self, user_input: str) -> None:
        """
        Executes a single conversational turn:
        1. Validates input
        2. Sends query to Gemini
        3. Prints response
        4. Sanitizes response text
        5. Sends status message to ESP32 WebSocket client
        6. Plays audio through local TTS (routes to Bluetooth speaker)

        Args:
            user_input: Raw string typed by the user in terminal.
        """
        clean_input = user_input.strip()
        if not clean_input:
            print("[PIPELINE] Empty prompt ignored.")
            return

        print("\n[PIPELINE] Sending prompt to Gemini...")
        start_time = time.time()
        
        # 1. Fetch AI text response
        response_text = self.gemini.generate_response(clean_input)
        latency = time.time() - start_time
        
        print(f"[PIPELINE] Response received in {latency:.2f} seconds.")
        print(f"\nGemini Response: {response_text}\n")
        # 2. Broadcast response immediately to phone dashboard so text displays instantly
        self.ws_server.broadcast_to_phones("status", {"action": "speaking", "text": response_text})
        self.ws_server.broadcast_to_phones("response", {
            "question": clean_input,
            "answer": response_text
        })

        # 3. Speak the response asynchronously in a background thread to prevent UI freezing
        import threading
        def speak_and_reset():
            self.audio.speak(response_text)
            self.ws_server.broadcast_to_phones("status", {"action": "idle"})

        threading.Thread(target=speak_and_reset, daemon=True).start()

    def close(self) -> None:
        """
        Cleanly stops background services (e.g. WebSocket and HTTP Servers).
        """
        print("[PIPELINE] Shutting down conversation pipeline...")
        if hasattr(self, 'web_server') and self.web_server:
            self.web_server.stop()
        if hasattr(self, 'ws_server') and self.ws_server:
            self.ws_server.stop()

