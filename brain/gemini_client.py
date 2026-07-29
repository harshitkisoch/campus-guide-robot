from google import genai
from google.genai import errors
from google.genai import types
from config.settings import settings

class GeminiClient:
    """
    Handles connectivity and interactions with Google's Gemini LLM.
    Uses credentials and settings supplied by the config module.
    """
    def __init__(self) -> None:
        """
        Initializes the Gemini Client with the API key from settings.
        """
        # Read verified credentials
        api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model

        # Instantiate official GenAI client
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt: str) -> str:
        """
        Sends the user text query to Gemini API and returns the text response.

        Args:
            prompt: Text statement or question.

        Returns:
            The text response from the model, or an error description.
        """
        if not prompt.strip():
            return "Prompt cannot be empty."

        try:
            # Query the AI model with strict instruction to keep it short (speeds up generation)
            config = types.GenerateContentConfig(
                system_instruction="You are a friendly guide robot at JECRC University. Answer in English or Hindi as requested. Keep your response extremely short, under 15 words, and in a single concise sentence.",
                max_output_tokens=60
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "Error: Gemini returned an empty response."

        except errors.APIError as e:
            # Handle standard API problems (authentication, rate limits, quota)
            error_msg = f"[Gemini API Error] {e.message} (Status: {e.code})"
            print(f"[ERROR] {error_msg}")
            return f"Sorry, I had an API issue: {e.message}"
            
        except Exception as e:
            # Handle connection losses or DNS drops
            error_msg = f"[Network Error] Could not connect to Gemini: {e}"
            print(f"[ERROR] {error_msg}")
            return "I am currently disconnected from my cloud server. Please check my network."
