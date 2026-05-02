from Backend.services.baseVoice import BaseVoiceService
from openai import OpenAI
import io
client = OpenAI()


class CloudVoiceService(BaseVoiceService):

    def transcribe(self, audio_bytes):

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.mp3"
        transcribed = client.audio.transcriptions.create(
            model= "gpt-4o-transcribe",
            file= audio_file

        )

        return transcribed.text

  