from .imports import *
from .GameStateManager import GameStateManager
from abc import ABC
from .utils import StaticSender

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *

class Flower(PressurePlate, ABC):
    def __init__(self, flower_name: str, image_name: str):
        super().__init__(f'flowers/{image_name}')
        self.flower_name = flower_name

    def player_entered(self, player) -> list[Message]:
        if hasattr(player, "is_hunter"): return []
        gsm = GameStateManager()
        gsm.collect_item("flower")
        
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position()) 
        
        return [ChatMessage(StaticSender("UPDATE"), room, f"You stepped on a {self.flower_name}! The hunter slows down...")]
    
class Daisy(Flower):
    def __init__(self):
        super().__init__('daisy', 'Daisy')

class Orchid(Flower):
    def __init__(self):
        super().__init__('orchid', 'Orchid')

class Daffodil(Flower):
    def __init__(self):
        super().__init__('daffodil', 'Daffodil')

class Tulip(Flower):
    def __init__(self):
        super().__init__('tulip', 'Tulip')


