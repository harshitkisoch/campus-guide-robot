import time
import re
from brain.gemini_client import GeminiClient
from communication.websocket_server import WebSocketServer
from audio.text_to_speech import TextToSpeech

class ConversationPipeline:
    """
    Orchestrates the entire AI conversation flow:
    Keyboard input -> Gemini Client API -> Laptop TTS (Bluetooth Speaker) & ESP32 WebSocket Status.
    """
    def __init__(self) -> None:
        """
        Initializes core modules needed for the conversation.
        """
        print("[PIPELINE] Initializing core modules...")
        self.gemini = GeminiClient()
        self.tts = TextToSpeech()
        
        # Initialize and start the WebSocket Server
        self.ws_server = WebSocketServer()
        self.ws_server.start()
            
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

        # 2. Sanitize the response (useful for status transmission)
        sanitized_text = self._sanitize_for_tts(response_text)
        print(f"[PIPELINE] Sanitized for ESP32: '{sanitized_text}'")

        # 3. Transmit "speaking" status to ESP32 wirelessly via WebSocket
        if self.ws_server.is_connected:
            print("[PIPELINE] Notifying ESP32 (speaking status)...")
            self.ws_server.send_message("status", {"action": "speaking", "text": sanitized_text})

        # 4. Speak the response (blocks until finished).
        # Plays automatically on the laptop's default audio output (your Bluetooth speaker).
        print("[PIPELINE] Speaking response...")
        self.tts.speak(response_text)
        print("[PIPELINE] Speech finished.")

        # 5. Transmit "idle" status back to ESP32
        if self.ws_server.is_connected:
            self.ws_server.send_message("status", {"action": "idle"})
            print("[PIPELINE] Notified ESP32 (idle status).")

    def _sanitize_for_tts(self, text: str) -> str:
        """
        Cleans the string so it only contains characters compatible with 
        the ESP32 SAM speech engine (ASCII alphanumeric and simple punctuation).
        Limits sentence length for vocal clarity.
        """
        # 1. Extract the first sentence to prevent long, robotic run-on speech
        sentences = text.split('.')
        first_sentence = sentences[0]
        
        # If the first segment is too short (e.g., "Yes."), try adding the second sentence
        if len(first_sentence.strip()) < 10 and len(sentences) > 1:
            first_sentence = first_sentence + ". " + sentences[1]
            
        # 2. Restrict length to 120 characters to fit SAM buffer limits
        truncated = first_sentence[:120].strip()
        
        # 3. Remove markdown symbols (asterisks, hashtags) and emojis
        # Keep only letters, numbers, spaces, and basic punctuation
        allowed_pattern = re.compile(r'[^a-zA-Z0-9\s.,!?]')
        sanitized = allowed_pattern.sub('', truncated)
        
        return sanitized

