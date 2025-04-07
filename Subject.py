from abc import ABC, abstractmethod

class Subject(ABC):
    @abstractmethod
    def add_observer(self, observer):
        pass
    
    @abstractmethod
    def remove_observer(self, observer):
        pass
    
    @abstractmethod
    def notify_observers(self, event):
        pass