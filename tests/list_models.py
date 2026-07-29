import sys
from pathlib import Path

# Add project root to python path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from api.gemini_client import GeminiClient

def list_available_models():
    """
    Queries Google Gemini API to list all models available for the configured API key.
    Helps developers discover which model names they can put in their .env file.
    """
    print("=== List Available Gemini Models ===")
    
    try:
        # Initialize client
        print("[INFO] Initializing GeminiClient...")
        gemini_wrapper = GeminiClient()
        client = gemini_wrapper.client
        
        print("[INFO] Fetching model list from Google AI Studio...")
        
        # Query Google's API to list models
        models = client.models.list()
        
        print("\nAvailable Models for your API Key:")
        print("-" * 60)
        
        count = 0
        for model in models:
            # We filter for models that support text generation (usually 'generateContent')
            if 'generateContent' in model.supported_generation_methods:
                # Strip the prefix 'models/' if present to show clean config name
                name_clean = model.name.replace("models/", "")
                print(f" - {name_clean:<25} | Description: {model.description or 'No description'}")
                count += 1
                
        print("-" * 60)
        print(f"Total generateContent-compatible models found: {count}")
        print("\n[TIP] Choose one of the names above (e.g., 'gemini-1.5-flash')")
        print("      and set GEMINI_MODEL=your_chosen_model in your .env file.")
        
    except Exception as e:
        print(f"\n[FAIL] Failed to list models: {e}")
        print("Please check that your GEMINI_API_KEY in the .env file is correct and active.")
        sys.exit(1)

if __name__ == "__main__":
    list_available_models()
