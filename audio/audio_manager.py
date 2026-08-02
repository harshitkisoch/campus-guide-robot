from config.settings import settings
from audio.base_output import BaseAudioOutput
from audio.bluetooth_output import BluetoothAudioOutput
from audio.esp32_output import ESP32AudioOutput
from audio.sarvam_output import SarvamAudioOutput
from communication.websocket_server import WebSocketServer

class AudioManager:
    """
    Factory and Router manager for the audio layer.
    Resolves the configuration value `OUTPUT_DEVICE` and instantiates the selected
    driver, exposing a unified `speak()` interface.
    """
    def __init__(self, ws_server: WebSocketServer) -> None:
        """
        Loads settings and instantiates the chosen audio output driver.
        
        Args:
            ws_server: The active WebSocketServer instance needed if ESP32 output is selected.
        """
        # Resolve device from settings (e.g. "bluetooth" or "esp32")
        self.device_name = settings.output_device.lower()
        self.driver: BaseAudioOutput = None

        if self.device_name == "esp32":
            self.driver = ESP32AudioOutput(ws_server)
        elif self.device_name == "sarvam":
            try:
                self.driver = SarvamAudioOutput()
            except Exception as e:
                print(f"[AUDIO MANAGER WARNING] Failed to initialize Sarvam TTS ({e}). Falling back to local Bluetooth audio.")
                self.driver = BluetoothAudioOutput()
                self.device_name = "bluetooth"
        else:
            # Default fallback is local Bluetooth/laptop sound card
            self.driver = BluetoothAudioOutput()

        print(f"[AUDIO MANAGER] Configured output channel: [{self.device_name.upper()}]")

    def speak(self, text: str) -> None:
        """
        Unified routing command to play speech text.
        
        Args:
            text: The text string to verbalize.
        """
        self.driver.speak(text)
