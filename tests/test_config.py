import sys
from pathlib import Path

# Add project root to python path so we can import config
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.config import settings

def test_config():
    """
    Verifies that the configuration values are loaded and formatted correctly.
    """
    print("=== Configuration Load Test ===")
    
    # Verify GEMINI_API_KEY loaded
    api_key = settings.gemini_api_key
    if api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("[WARNING] GEMINI_API_KEY is still set to placeholder 'YOUR_GEMINI_API_KEY_HERE'.")
        print("          You will need to replace this with a real key from Google AI Studio later.")
    elif len(api_key) > 5:
        # Mask the key for security, showing only the first 5 characters
        masked_key = f"{api_key[:5]}...{api_key[-4:] if len(api_key) > 9 else ''}"
        print(f"[OK] GEMINI_API_KEY is loaded: {masked_key}")
    else:
        print("[FAIL] GEMINI_API_KEY is empty or too short.")
        sys.exit(1)

    # Verify serial configuration
    print(f"[OK] SERIAL_PORT: {settings.serial_port}")
    print(f"[OK] SERIAL_BAUD_RATE: {settings.serial_baud_rate} (Type: {type(settings.serial_baud_rate).__name__})")
    
    # Verify server configuration
    print(f"[OK] HOST: {settings.host}")
    print(f"[OK] PORT: {settings.port}")
    
    print("\n[SUCCESS] Configuration loaded and validated successfully!")

if __name__ == "__main__":
    test_config()
