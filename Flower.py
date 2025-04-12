from enum import Enum
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


# Define the enum for flower names
class FlowerName(Enum):
    DAISY = "daisy"
    ORCHID = "orchid"
    DAFFODIL = "daffodil"
    TULIP = "tulip"


class Flower(PressurePlate, ABC):
    def __init__(self, flower_name: str, image_name: str = None) -> None:
        """
        Initialize a Flower with a given name and image.
        
        Preconditions:
            - flower_name must be an instance of FlowerName.
            - If image_name is not provided, it defaults to the flower_name's enum value.
        """
        assert flower_name is not None, "Precondition failed: 'flower_name' cannot be None."
        
        # Use the provided image_name or default to the enum's value
        image = f'flowers/{image_name or flower_name.value}'
        super().__init__(image)
        self.flower_name: FlowerName = flower_name

    def player_entered(self, player) -> list[Message]:
        """
        Handles a player stepping on the flower's pressure plate.
        
        Preconditions:
            - The 'player' argument must not be None.
            - 'player' must have a 'get_current_room()' method that returns a room with a 'remove_from_grid()' method.
            - If the player has an attribute 'is_hunter', the flower does not affect game state/it doen't collect the flower.

        Postconditions:
            - The game state is updated by collecting the flower.
            - The flower is removed from the room's grid.
            - The flower is appended to the player's inventory.
            - A ChatMessage describing the effect (slowing down the hunter) is returned.
        
        :param player: The player interacting with the flower.
        :return: A list of Message objects indicating the outcome.
        """
        assert player is not None, "Precondition failed: 'player' cannot be None."
        assert hasattr(player,"get_current_room"), "Precondition failed: 'player' must have 'get_current_room()' method."

        if hasattr(player, "is_hunter"): return []
        gsm = GameStateManager()
        gsm.collect_item("flower")
        
        coord: Coord = self.get_position()
        gsm.track_picked_item(self, coord)

        room = player.get_current_room()
        assert hasattr(room, "remove_from_grid"), "Precondition failed: room must have 'remove_from_grid()' method."
        room.remove_from_grid(self, self.get_position()) 

        if not hasattr(player, "inventory"):
            player.inventory = []
        player.inventory.append(self)

        
        return [ChatMessage(StaticSender("UPDATE"), room, f"You stepped on a {self.flower_name.value}! The hunter slows down...")]
    
class Daisy(Flower):
    def __init__(self):
        super().__init__(FlowerName.DAISY)

class Orchid(Flower):
    def __init__(self):
        super().__init__(FlowerName.ORCHID)

class Daffodil(Flower):
    def __init__(self):
        super().__init__(FlowerName.DAFFODIL)

class Tulip(Flower):
    def __init__(self):
        super().__init__(FlowerName.TULIP)


