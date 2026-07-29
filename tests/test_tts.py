import sys
from pathlib import Path

# Add project root to python path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from audio.text_to_speech import TextToSpeech

def test_tts_engine() -> None:
    """
    Test script to verify offline Text-To-Speech synthesis.
    """
    print("=== Testing Local Offline TTS Component ===")
    
    try:
        print("[INFO] Initializing TextToSpeech engine...")
        tts = TextToSpeech()
        
        test_phrase = "Hello fresher! I am your campus guide robot. Text to speech engine is working perfectly."
        print(f"[INFO] Speaking text: '{test_phrase}'")
        
        # Speak the test phrase (should hear voice output on laptop speakers)
        tts.speak(test_phrase)
        
        print("[SUCCESS] Text-To-Speech audio test completed!")
        
    except Exception as e:
        print(f"\n[FAIL] TTS test failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_tts_engine()
