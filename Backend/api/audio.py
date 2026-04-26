from fastapi import APIRouter,UploadFile,File,Depends
from services.base import BaseVoiceService
from services.factory import get_voice_service


audio_router = APIRouter()


@audio_router.post("/speech-to-text")
async def speech_to_text(file : UploadFile = File(...), service : BaseVoiceService = Depends(get_voice_service)):
    
    audio_bytes = await file.read()

    text = service.transcribe(audio_bytes)

    return {"text" : text}