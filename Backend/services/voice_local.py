from Backend.services.baseVoice import BaseVoiceService
import numpy as np
from  faster_whisper import WhisperModel


model_size = "small"


class LocalWhisperService(BaseVoiceService):

    def __init__(self):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_bytes):

        audio = np.frombuffer(audio_bytes,dtype=np.int16).astype(np.float32) / 32768.0 

        

        segments,info = self.model.transcribe(audio,task="translate")
        text = ""
        for segment in segments :
            text += segment.text


        return text