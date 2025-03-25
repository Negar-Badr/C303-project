from .imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from message import SenderInterface

class StaticSender(SenderInterface):
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name
