from abc import ABC , abstractmethod
from PIL import Image
from schemas.taskBody import GenerationTask
class BaseFluxService(ABC):

    @abstractmethod
    def generate(self,task : GenerationTask) -> Image:
        """
            Must return:
            - PIL image 
        """
        pass