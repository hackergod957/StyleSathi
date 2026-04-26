from dotenv import load_dotenv
import os
from core.AppException import AppException
from services.voice_local import LocalWhisperService
from services.voice_cloud import CloudVoiceService

load_dotenv()

def get_voice_service():
    mode = os.getenv("VOICE_SERVICE_TYPE")

    if mode == "local":
        ''' call the local model service'''

        return LocalWhisperService()
        
    elif mode == "cloud":
        '''call the open wishper api cloud service'''

        return CloudVoiceService()
    
    else:
        raise AppException("Invalid Mode of Voice Service")