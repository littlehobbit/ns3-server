from abc import ABC, abstractmethod
from typing import List


class UploadError(RuntimeError):
    pass

class Uploader(ABC):
    """ Abstract interface for uploading results of simulation to storage """

    @abstractmethod
    def upload(self, results: str) -> str:
        """ zip & upload result directory """
        pass
