import re
import pyttsx3
from audio.base_output import BaseAudioOutput
from config.settings import settings

class BluetoothAudioOutput(BaseAudioOutput):
    """
    Audio driver that outputs speech locally via the laptop's default 
    sound interface (which routes to a paired Bluetooth speaker) using pyttsx3.
    """
    def __init__(self) -> None:
        """
        Initializes the driver state.
        """
        print("[AUDIO] Local Bluetooth Audio driver initialized.")

    def speak(self, text: str) -> None:
        """
        Synthesizes text locally on the laptop. 
        Implements dynamic engine init to bypass pyttsx3 event loop crashes.
        """
        if not text.strip():
            return

        try:
            # 1. Initialize a clean pyttsx3 instance for this statement
            engine = pyttsx3.init('sapi5')
            
            # 2. Set rate and volume
            engine.setProperty('rate', settings.tts_rate)
            engine.setProperty('volume', settings.tts_volume)
            
            # 3. Bilingual voice selection
            voices = engine.getProperty('voices')
            hindi_voice = None
            english_voice = None
            
            for v in voices:
                name_lower = v.name.lower()
                id_lower = v.id.lower()
                if "hindi" in name_lower or "india" in name_lower or "kalpana" in name_lower or "1081" in id_lower:
                    hindi_voice = v
                elif "zira" in name_lower or "hazel" in name_lower or "english" in name_lower:
                    english_voice = v

            # Default fallback if Zira is missing
            if not english_voice and len(voices) > 0:
                english_voice = voices[0]
                
            is_hindi = self._detect_hindi_context(text)
            
            if is_hindi and hindi_voice:
                engine.setProperty('voice', hindi_voice.id)
                print(f"[TTS] Speaking with Hindi voice: {hindi_voice.name}")
            else:
                selected_voice = english_voice if english_voice else (voices[0] if voices else None)
                if selected_voice:
                    engine.setProperty('voice', selected_voice.id)
                    print(f"[TTS] Speaking with English voice: {selected_voice.name}")

            # 4. Play speech (blocks thread until complete)
            engine.say(text)
            engine.runAndWait()
            
            # 5. Clean up SAPI5 engine
            engine.stop()
            del engine
            
        except Exception as e:
            print(f"[ERROR] Bluetooth Audio playback failure: {e}")

    def _detect_hindi_context(self, text: str) -> bool:
        """
        Helper: Detects if the context contains Hindi/Hinglish words.
        """
        if re.search(r'[\u0900-\u097F]', text):
            return True
            
        hinglish_keywords = {
            "main", "aap", "kaise", "bataiye", "hoon", "hai", "swagat", 
            "namaste", "achha", "accha", "kar", "sakta", "kya", "madad", 
            "mera", "naam", "jecrc", "university", "freshers"
        }
        
        words = set(re.findall(r'\b\w+\b', text.lower()))
        return len(words.intersection(hinglish_keywords)) >= 2
