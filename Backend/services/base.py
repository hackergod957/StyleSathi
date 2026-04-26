from abc import ABC , abstractmethod

class BaseVoiceService(ABC):

    @abstractmethod
    def transcribe(self , audio_bytes : bytes) -> str:
        """
        Convert raw audio bytes into English text.

        Args:
            audio_bytes (bytes): Audio data (WAV/PCM/etc.)

        Returns:
            str: Transcribed English text
        """

        pass

