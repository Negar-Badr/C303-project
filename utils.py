from .imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from message import SenderInterface

class StaticSender(SenderInterface):
    def __init__(self, name: str) -> None:
        """
        Initialize a StaticSender with a given name.
        
        Preconditions:
            - name must be a non-empty string.
        """
        assert isinstance(name, str) and name, "name must be a non-empty string."
        self.name: str = name

    def get_name(self) -> str:
        """
        Retrieve the static sender's name.
        
        Postconditions:
            - Returns a non-empty string representing the sender's name.
        """
        result: str = self.name
        assert isinstance(result, str) and result, "Sender's name must be a non-empty string."
        return result
