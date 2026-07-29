import re
import pyttsx3
from config.settings import settings

class TextToSpeech:
    """
    Offline Text-To-Speech engine using pyttsx3.
    Operates locally, utilizing Windows native SAPI5 speech synthesis.
    Implements dynamic engine initialization to prevent event loop hanging.
    Supports smart bilingual switching between Hindi (Kalpana) and English (Zira).
    """
    def __init__(self) -> None:
        """
        Initializes the TTS settings reference.
        """
        print("[TTS] Initialized local speaker system.")

    def speak(self, text: str) -> None:
        """
        Speaks the given text out loud.
        Dynamically detects language context (English or Hindi) and configures
        the appropriate native voice.
        """
        if not text.strip():
            return

        try:
            # 1. Initialize a fresh engine instance for this specific sentence
            engine = pyttsx3.init('sapi5')
            
            # 2. Configure speaking speed rate
            engine.setProperty('rate', settings.tts_rate)
            
            # 3. Configure speaking volume level
            engine.setProperty('volume', settings.tts_volume)
            
            # 4. Bilingual Voice Selection Logic
            voices = engine.getProperty('voices')
            
            # Find candidate voices in the system
            hindi_voice = None
            english_voice = None
            
            for v in voices:
                name_lower = v.name.lower()
                id_lower = v.id.lower()
                
                # Check for Hindi voice (Microsoft Kalpana is standard on Windows)
                if "hindi" in name_lower or "india" in name_lower or "kalpana" in name_lower or "1081" in id_lower:
                    hindi_voice = v
                # Check for English voice (Microsoft Zira or Hazel)
                elif "zira" in name_lower or "hazel" in name_lower or "english" in name_lower:
                    english_voice = v

            # Default fallbacks if specific matches aren't found
            if not english_voice and len(voices) > 0:
                english_voice = voices[0]
                
            # Detect if the response is in Hindi or Hinglish
            is_hindi = self._detect_hindi_context(text)
            
            if is_hindi and hindi_voice:
                engine.setProperty('voice', hindi_voice.id)
                print(f"[TTS] Speaking with Hindi voice: {hindi_voice.name}")
            else:
                # Fallback to English Zira
                selected_voice = english_voice if english_voice else (voices[0] if voices else None)
                if selected_voice:
                    engine.setProperty('voice', selected_voice.id)
                    print(f"[TTS] Speaking with English voice: {selected_voice.name}")

            # 5. Play the speech segment (blocks until sentence completes)
            engine.say(text)
            engine.runAndWait()
            
            # 6. Stop and clean up the engine instance
            engine.stop()
            del engine
            
        except Exception as e:
            print(f"[ERROR] TTS synthesis runtime failure: {e}")

    def _detect_hindi_context(self, text: str) -> bool:
        """
        Detects if the text context contains Hindi script or common Hinglish words.
        """
        # Case 1: Check for Devanagari script (Hindi characters)
        if re.search(r'[\u0900-\u097F]', text):
            return True
            
        # Case 2: Check for common Hinglish vocabulary words
        hinglish_keywords = {
            "main", "aap", "kaise", "bataiye", "hoon", "hai", "swagat", 
            "namaste", "achha", "accha", "kar", "sakta", "kya", "madad", 
            "mera", "naam", "jecrc", "university", "freshers"
        }
        
        words = set(re.findall(r'\b\w+\b', text.lower()))
        # If there's an overlap of common Hinglish words, switch to Hindi voice
        if len(words.intersection(hinglish_keywords)) >= 2:
            return True
            
        return False
