import sys
from pathlib import Path

# Add project root to python path so we can import config
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import settings

def test_settings_load() -> None:
    """
    Verifies settings.py loads and validates environment variables.
    """
    print("=== Testing Configuration Settings ===")
    
    # 1. Check Gemini Key (must not be empty, must be masked for print)
    key = settings.gemini_api_key
    if not key or key == "YOUR_GEMINI_API_KEY_HERE":
        print("[FAIL] GEMINI_API_KEY is not configured or still set to placeholder.")
        sys.exit(1)
        
    masked_key = f"{key[:4]}************{key[-4:] if len(key) > 8 else ''}"
    print(f"[OK] GEMINI_API_KEY loaded: {masked_key}")
    
    # 2. Check Model Name
    print(f"[OK] GEMINI_MODEL: {settings.gemini_model}")
    
    # 3. Check TTS settings
    print(f"[OK] TTS_RATE: {settings.tts_rate} (Type: {type(settings.tts_rate).__name__})")
    print(f"[OK] TTS_VOLUME: {settings.tts_volume} (Type: {type(settings.tts_volume).__name__})")
    
    print("\n[SUCCESS] config/settings.py unit test passed!")

if __name__ == "__main__":
    test_settings_load()
