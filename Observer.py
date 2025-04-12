from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def on_notify(self, event: str) -> None:
        """
        Handle notifications from the subject.

        Preconditions:
            - event must be a non-empty string representing the notification event.
        """
        pass