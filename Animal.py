from .imports import *
from .GameStateManager import GameStateManager
from abc import ABC
from .utils import StaticSender
from .Observer import Observer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *

class Animal(PressurePlate, Observer, ABC):
    def __init__(self, animal_name: str, image_name: str):
        super().__init__(f'animals/{image_name}')
        self.animal_name = animal_name

    #TODO
    def on_notify(self, subject, event):
        pass

    def player_entered(self, player) -> list[Message]:
        if hasattr(player, "is_hunter"): return []
        gsm = GameStateManager()
        gsm.collect_animal(self.animal_name)

        coord = self.get_position()
        gsm.track_picked_item(self, coord)

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())

        if not hasattr(player, "inventory"):
            player.inventory = []
        player.inventory.append(self)


        return [ChatMessage(StaticSender("UPDATE"), room, f"You rescued a {self.animal_name}! ({gsm.collected_animals}/{gsm.total_animals})")]
    
class Cow(Animal):
    def __init__(self):
        super().__init__('cow', 'cow')

class Monkey(Animal):
    def __init__(self):
        super().__init__('monkey', 'monkey')

class Owl(Animal):
    def __init__(self):
        super().__init__('owl', 'owl')

class Rabbit(Animal):
    def __init__(self):
        super().__init__('rabbit', 'rabbit')
