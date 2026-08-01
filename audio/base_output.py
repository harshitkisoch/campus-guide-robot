from abc import ABC, abstractmethod

class BaseAudioOutput(ABC):
    """
    Abstract base class representing an audio output channel.
    All physical audio drivers (Bluetooth, ESP32 DAC, USB) must
    inherit from this class and implement the speak() method.
    """

    @abstractmethod
    def speak(self, text: str) -> None:
        """
        Takes a text string, synthesizes it (or transmits it for synthesis),
        and outputs it as speech.
        Blocks the execution thread during playback to prevent overlapping voice prompts.

        Args:
            text: The text statement to verbalize.
        """
        pass
