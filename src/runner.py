from abc import ABC, abstractmethod


class Runner(ABC):
    """ Class for running simulation and provice access to logs and so on """

    @abstractmethod
    def run(self,   cwd: str):
        pass

    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def stop(self):
        pass
