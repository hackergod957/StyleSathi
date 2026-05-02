from PIL import Image
from services.baseFlux import BaseFluxService
import requests
import base64
import io

class ColabFluxService(BaseFluxService):
     
     def __init__(self,url):
        self.url = url
   
     def generate(self,task):


        payload = {
            "image" : task.image,
            "mask" : task.mask,
            "prompt" : task.prompt
         }
        
        response = requests.post(
            self.url,
            json = payload,
            timeout=120
        )

        data = response.json()
        image_base64 = data["image"]

        image_bytes  = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))

        return image