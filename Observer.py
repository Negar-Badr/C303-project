from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def on_notify(self, event):
        """Handle notifications from the subject."""
        pass