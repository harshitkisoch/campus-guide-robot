import os
import base64
import tempfile
import requests
from audio.base_output import BaseAudioOutput
from config.settings import settings

class SarvamAudioOutput(BaseAudioOutput):
    """
    Hindi Text-to-Speech output driver using the Sarvam AI bulbul:v3 API.
    Converts text to natural Hindi speech audio, saves as a temp WAV file,
    and plays it through the system default audio output device.
    """

    API_URL = "https://api.sarvam.ai/text-to-speech"

    def __init__(self) -> None:
        self.api_key = settings.sarvam_api_key
        if not self.api_key:
            raise ValueError("[SARVAM] No Sarvam API key found. Set SARVAM_API_KEY in your .env file.")
        print("[SARVAM TTS] Hindi voice engine initialized (bulbul:v3).")

    def speak(self, text: str) -> None:
        """
        Sends text to the Sarvam TTS API, receives base64-encoded WAV audio,
        decodes it, saves to a temp file, and plays it using the OS default player.
        """
        if not text.strip():
            return

        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "language_code": "hi-IN",
            "speaker": "priya",
            "model": "bulbul:v3",
            "pace": 1.0
        }

        try:
            print(f"[SARVAM TTS] Generating Hindi speech for: \"{text[:60]}...\"")
            response = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                audio_base64 = data["audios"][0]

                # Decode base64 audio to raw WAV bytes
                audio_bytes = base64.b64decode(audio_base64)

                # Write to a temp WAV file and play it
                temp_path = os.path.join(tempfile.gettempdir(), "sarvam_speech.wav")
                with open(temp_path, "wb") as f:
                    f.write(audio_bytes)

                print(f"[SARVAM TTS] Playing Hindi audio...")
                try:
                    import winsound
                    winsound.PlaySound(temp_path, winsound.SND_FILENAME)
                except Exception as play_err:
                    print(f"[SARVAM TTS WARNING] winsound error ({play_err}), attempting system command playback...")
                    os.system(f'start /min "" "{temp_path}"')
                finally:
                    # Clean up temporary WAV file after playback
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception:
                        pass

            else:
                print(f"[SARVAM TTS ERROR] API returned {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            print("[SARVAM TTS ERROR] API request timed out.")
        except Exception as e:
            print(f"[SARVAM TTS ERROR] Failed to generate speech: {e}")
