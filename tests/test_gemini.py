import sys
from pathlib import Path

# Add project root to python path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from brain.gemini_client import GeminiClient

def test_gemini_connection() -> None:
    """
    Test script to verify communication with Google's Gemini API.
    """
    print("=== Testing Gemini Client Component ===")
    
    try:
        print("[INFO] Initializing GeminiClient...")
        client = GeminiClient()
        
        prompt = "Hello"
        print(f"[INFO] Sending test prompt: '{prompt}'")
        
        response = client.generate_response(prompt)
        
        print("\n=== Gemini Response ===")
        print(response)
        print("=======================\n")
        
        if "API Error" in response or "Network Error" in response or "disconnected" in response:
            print("[FAIL] Gemini client returned an error response.")
            sys.exit(1)
        else:
            print("[SUCCESS] Gemini Client integration test passed!")
            
    except Exception as e:
        print(f"\n[FAIL] Test failed with unexpected exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_gemini_connection()
