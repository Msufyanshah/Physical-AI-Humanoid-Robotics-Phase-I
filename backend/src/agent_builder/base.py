from abc import ABC, abstractmethod

class BaseAgentRunner(ABC):
    @abstractmethod
    def run(self, input: dict):
        pass
