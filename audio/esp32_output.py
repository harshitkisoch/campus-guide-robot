import re
from audio.base_output import BaseAudioOutput
from communication.websocket_server import WebSocketServer

class ESP32AudioOutput(BaseAudioOutput):
    """
    Audio driver that transmits text payloads wirelessly over WebSockets 
    to the ESP32 (which synthesizes it offline and plays it via the HW-104 amplifier).
    """
    def __init__(self, ws_server: WebSocketServer) -> None:
        """
        Initializes the ESP32 audio output channel with the active WebSocket server instance.
        """
        self.ws_server = ws_server
        print("[AUDIO] ESP32 HW-104 Audio driver initialized.")

    def speak(self, text: str) -> None:
        """
        Sends the text payload over WebSockets to the ESP32 after running SAM sanitization.
        """
        if not text.strip():
            return

        # Encapsulated hardware-specific sanitization
        sanitized = self._sanitize_for_sam(text)

        if self.ws_server.is_connected:
            print(f"[AUDIO] Transmitting speech payload: '{sanitized}'")
            self.ws_server.send_speech(sanitized)
        else:
            print("[AUDIO ERROR] Cannot play speech: ESP32 WebSocket client is offline.")
            print(f"[FALLBACK LOG] Intended text: '{text}'")

    def _sanitize_for_sam(self, text: str) -> str:
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
