from abc import ABC, abstractmethod

from enum import Enum, auto


class Status(Enum):
    START = auto(),
    UPLOADED = auto(),
    LOG = auto(),
    ERROR = auto(),
    END = auto()


class Notifier(ABC):
    @abstractmethod
    def send(self, status: Status, msg: str = ''):
        pass
