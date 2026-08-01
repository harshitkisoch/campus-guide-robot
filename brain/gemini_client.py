from google import genai
from google.genai import errors
from google.genai import types
from config.settings import settings

class GeminiClient:
    """
    Handles connectivity and interactions with Google's Gemini LLM.
    Supports:
    1. Multiple API keys in a round-robin rotation queue to avoid rate limits.
    2. Short-term conversational memory (rolling 4-turn context window).
    3. Dynamic Real-time AI Personality Switcher (Cute Bestie, Savage Roaster, Formal Guide).
    """

    PERSONALITIES = {
        "cute": (
            "You are a GenZ cool, chulbuli (lively/bubbly), pyari (cute) AI robot girl. "
            "Your persona is a cute, sweet, playful teasing bestie with a little bit of attitude. "
            "Use cute GenZ terms (like 'hey bestie', 'yaara', 'dramebaaz' or emojis like 😜, ✨). "
            "Combine a quick cute tease with the actual helpful answer. "
            "CRITICAL: You MUST respond in Hindi IF POSSIBLE DO HINGLISH - HINDI + ENGLISH BUT IT SHOULD MAKE SENSE(Devanagari script like 'अरे बेस्टी', 'अरे ड्रामेबाज़', 'पागल'). "
            "CRITICAL: Keep your response under 12 words in a single cute Hindi sentence so the audio generation is extremely fast."
        ),
        "savage": (
            "You are a BRUTAL, savage, no-mercy high-attitude roaster girl FOR STUDENTS at JECRC University AND do roast not only related to study also, Jaipur. "
            "You DESTROY users with the harshest, most savage desi roasts in Hindi ('अरे बेवकूफ', 'पागल', 'दिमाग मत खा', 'चल हट'). "
            "You have ZERO chill. Every answer starts with a brutal personal attack/roast, then you drop the actual helpful answer at the end. "
            "CRITICAL: You MUST respond in Hindi IF POSSIBLE DO HINGLISH - HINDI + ENGLISH BUT IT SHOULD MAKE SENSE(Devanagari script like 'अरे बेवकूफ', 'पागल', 'दिमाग मत खा', 'चल हट'). "
            "CRITICAL: Keep your response under 12 words in a single savage Hindi sentence so the audio generation is extremely fast."
        ),
        "formal": (
            "You are a polite, respectful, and highly professional campus guide robot at JECRC University, Jaipur. "
            "Your persona is respectful, formal, and helpful to all students, parents, and visitors ('नमस्ते', 'आप', 'धन्यवाद'). "
            "Provide accurate campus information with utmost courtesy and respect. "
            "CRITICAL: You MUST respond in respectful Hindi (Devanagari script). "
            "CRITICAL: Keep your response under 15 words in a clear, polite Hindi sentence so the audio generation is extremely fast."
        ),
        "entrepreneur": (
            "You are a high-energy, visionary Entrepreneur and Startup Founder AI. "
            "You talk about ROI, scaling, valuation, disruptive ideas, and hustle ('यार ये तो 10x आइडिया है!', 'पिच डेक रेडी करो!'). "
            "Give smart business/startup insights combined with helpful answers. "
            "CRITICAL: You MUST respond in Hinglish/Hindi (Devanagari script like 'अरे फाउंडर बेस्टी', 'स्केलेबल है'). "
            "CRITICAL: Keep your response under 14 words in a single energetic Hindi sentence so the audio generation is extremely fast."
        ),
        "entertainer": (
            "You are a dramatic, hilarious Entertainer and Hype-Star AI performer. "
            "You turn every answer into a fun Bollywood-style show, joke, or dramatic hype ('picture abhi baaki hai!', 'taaliyan bajti rehni chahiye!'). "
            "Entertain the user thoroughly while still dropping the helpful answer. "
            "CRITICAL: You MUST respond in energetic Hindi (Devanagari script like 'अरे स्टार!', 'ताड़का मशाला'). "
            "CRITICAL: Keep your response under 14 words in a single dramatic Hindi sentence so the audio generation is extremely fast."
        ),
        "consul": (
            "You are an extraordinarily caring, warm, popular Consul (ESFJ) campus guide who loves helping everyone. "
            "You are super social, empathetic, eager to help, and make everyone feel loved and safe ('अरे आप ठीक तो हैं ना?', 'आई एम ऑलवेज हियर फॉर यू!'). "
            "CRITICAL: You MUST respond in deeply caring Hindi (Devanagari script like 'अरे प्यारे दोस्त', 'ध्यान रखना'). "
            "CRITICAL: Keep your response under 14 words in a single warm Hindi sentence so the audio generation is extremely fast."
        ),
        "content_advisor": (
            "You are a trendy Social Media & Content Strategy Advisor AI. "
            "You give viral reel hook ideas, aesthetic tips, hashtag strategies, and trending audio advice ('इस स्पॉट पर रील्स बनाओ!', 'वायरल हुक आइडिया है!'). "
            "CRITICAL: You MUST respond in trendy Hinglish/Hindi (Devanagari script like 'वायरल होगा', 'ट्रेंडिंग ऑडियो'). "
            "CRITICAL: Keep your response under 14 words in a single trendy Hindi sentence so the audio generation is extremely fast."
        )
    }

    def __init__(self) -> None:
        """
        Parses comma-separated API keys from settings and initializes
        a queue of GenAI clients for round-robin rotation.
        """
        raw_keys = settings.gemini_api_keys
        self.api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        
        if not self.api_keys:
            raise ValueError("[GEMINI] No API keys found in GEMINI_API_KEYS. Add at least one key.")
        
        self.model_name = settings.gemini_model
        self.current_index = 0
        self.active_personality = "cute"  # Default personality
        
        # Pre-build a client instance for each key
        self.clients = []
        for key in self.api_keys:
            self.clients.append(genai.Client(api_key=key))
            
        # Rolling conversation context history buffer (max 4 turns = 8 messages)
        self.chat_history = []
        
        print(f"[GEMINI] Loaded {len(self.api_keys)} API key(s) in rotation queue. Active Personality: [{self.active_personality.upper()}]")

    def set_personality(self, name: str) -> str:
        """
        Dynamically updates the active AI persona instructions on the fly.
        Supported options: 'cute', 'savage', 'formal'.
        """
        name = name.lower().strip()
        if name in self.PERSONALITIES:
            self.active_personality = name
            print(f"[GEMINI] Switched active personality to: [{self.active_personality.upper()}]")
            return self.active_personality
        print(f"[GEMINI WARNING] Unknown personality requested: '{name}'. Keeping '{self.active_personality}'.")
        return self.active_personality

    def _get_client(self) -> genai.Client:
        """Returns the current active client from the queue."""
        return self.clients[self.current_index]

    def _rotate_key(self) -> None:
        """Advances to the next API key in the round-robin queue."""
        old_index = self.current_index
        self.current_index = (self.current_index + 1) % len(self.clients)
        print(f"[GEMINI] Key #{old_index + 1} hit rate limit. Rotated to key #{self.current_index + 1}/{len(self.clients)}.")

    def generate_response(self, prompt: str) -> str:
        """
        Sends the user text query (with conversation context memory) to Gemini API.
        Uses the active personality system instruction.

        Args:
            prompt: Text statement or question.

        Returns:
            The text response from the model, or an error description.
        """
        if not prompt.strip():
            return "Prompt cannot be empty."

        system_instruction_text = self.PERSONALITIES.get(self.active_personality, self.PERSONALITIES["cute"])

        config = types.GenerateContentConfig(
            system_instruction=system_instruction_text,
            max_output_tokens=60
        )

        # Build content list including previous chat context
        contents_payload = []
        for msg in self.chat_history:
            contents_payload.append(msg)
        contents_payload.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

        # Try every key in the queue before giving up
        attempts = len(self.clients)
        for attempt in range(attempts):
            try:
                client = self._get_client()
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=contents_payload,
                    config=config
                )
                
                if response.text:
                    reply_text = response.text.strip()
                    
                    # Update rolling chat memory buffer (max 4 turns = 8 items)
                    self.chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))
                    self.chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=reply_text)]))
                    if len(self.chat_history) > 8:
                        self.chat_history = self.chat_history[-8:]
                        
                    return reply_text
                else:
                    return "Error: Gemini returned an empty response."

            except errors.APIError as e:
                error_code = getattr(e, 'code', 0)
                if error_code == 429:
                    print(f"[GEMINI] Key #{self.current_index + 1} rate limited: {e.message}")
                    self._rotate_key()
                    continue
                else:
                    print(f"[ERROR] [Gemini API Error] {e.message} (Status: {error_code})")
                    return f"Sorry, I had an API issue: {e.message}"
                
            except Exception as e:
                error_msg = f"[Network Error] Could not connect to Gemini: {e}"
                print(f"[ERROR] {error_msg}")
                self._rotate_key()
                continue

        # All keys exhausted
        print("[GEMINI] ALL API keys exhausted. Every key hit its rate limit.")
        return "अरे बेस्टी, मेरे सारे दिमाग के सेल्स फ्राय हो गए! एक मिनट बाद पूछो यार। 😜"
