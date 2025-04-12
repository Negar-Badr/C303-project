from abc import ABC, abstractmethod
from .Observer import Observer  

class Subject(ABC):
    @abstractmethod
    def add_observer(self, observer: Observer) -> None:
        """
        Add an observer to the subject.

        Preconditions:
            - observer must be a non-None instance of Observer.
            
        Postconditions:
            - The observer is registered with the subject, and future notifications will include it.
        """
        pass

    @abstractmethod
    def remove_observer(self, observer: Observer) -> None:
        """
        Remove an observer from the subject.

        Preconditions:
            - observer must be a non-None instance of Observer that is already registered.
            
        Postconditions:
            - The observer is unregistered from the subject.
        """
        pass

    @abstractmethod
    def notify_observers(self, event: str) -> None:
        """
        Notify all registered observers of an event.

        Preconditions:
            - event must be a non-empty string representing the notification event.
            
        Postconditions:
            - Each registered observer's on_notify method is called with the given event.
        """
        pass