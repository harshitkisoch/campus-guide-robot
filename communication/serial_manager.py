import time
import serial
from config.settings import settings

class SerialManager:
    """
    Manages robust physical USB serial communication with the ESP32.
    Implements error handling, connection detection, and auto-reconnection.
    """
    def __init__(self, port: str = None) -> None:
        """
        Initializes the serial settings.
        
        Args:
            port: Optional COM port string to override the configuration file.
        """
        # Load from Settings if not explicitly overridden (useful for testing override)
        self.port = port if port else settings.serial_port
        self.baud_rate = settings.serial_baud_rate
        
        self.connection = None
        self.is_connected = False
        print(f"[SERIAL] Manager initialized for port {self.port} at {self.baud_rate} baud.")

    def connect(self) -> bool:
        """
        Attempts to open the serial port connection safely.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        if self.is_connected and self.connection and self.connection.is_open:
            return True

        try:
            print(f"[SERIAL] Attempting to connect to {self.port}...")
            # 1. Open the port with a 2-second timeout to prevent locking up the thread
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=2.0,
                write_timeout=2.0
            )
            self.is_connected = True
            print(f"[SERIAL] Connected successfully to {self.port}.")
            
            # Give the ESP32 chip a moment to reset after the port opens
            time.sleep(1.5)
            # Flush buffers to clear garbage boot characters
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
            return True
            
        except serial.SerialException as e:
            print(f"[SERIAL ERROR] Failed to connect to port {self.port}: {e}")
            self.is_connected = False
            self.connection = None
            return False

    def write_message(self, message: str) -> bool:
        """
        Writes a text message to the serial port. Appends a newline terminator.
        Automatically handles reconnection if port has closed.

        Args:
            message: The string to transmit.

        Returns:
            True if transmission succeeded, False if failed.
        """
        # Ensure we are connected
        if not self.is_connected or not self.connection or not self.connection.is_open:
            print("[SERIAL] Not connected. Attempting automatic reconnection...")
            if not self.connect():
                return False

        try:
            # 1. Add newline delimiter to show end of command to ESP32
            formatted_msg = f"{message}\n"
            # 2. Convert string to raw bytes and write to hardware buffer
            self.connection.write(formatted_msg.encode('utf-8'))
            self.connection.flush() # Wait until transmission complete
            return True
        except (serial.SerialException, AttributeError) as e:
            print(f"[SERIAL ERROR] Write failed: {e}. Mark connection as lost.")
            self.close()
            return False

    def read_line(self) -> str:
        """
        Reads a line of text from the serial buffer (until '\n').

        Returns:
            The decoded response string, or empty string on timeout/failure.
        """
        if not self.is_connected or not self.connection or not self.connection.is_open:
            return ""

        try:
            # Read line from serial buffer (decodes raw bytes to UTF-8 string, ignoring invalid bootloader bytes)
            line_bytes = self.connection.readline()
            line = line_bytes.decode('utf-8', errors='ignore').strip()
            return line
        except Exception as e:
            print(f"[SERIAL ERROR] Read failed: {e}.")
            self.close()
            return ""

    def close(self) -> None:
        """
        Closes the active serial connection safely.
        """
        self.is_connected = False
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
                print(f"[SERIAL] Port {self.port} closed safely.")
            except Exception:
                pass
        self.connection = None
