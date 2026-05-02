from pydantic import BaseModel

class GenerationTask(BaseModel):
    image : str
    mask : str
    prompt : str
