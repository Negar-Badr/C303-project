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


# Define the enum for animal names
class AnimalName(Enum):
    COW = "cow"
    MONKEY = "monkey"
    OWL = "owl"
    RABBIT = "rabbit"

class Animal(PressurePlate, ABC):
    def __init__(self, animal_name: AnimalName, image_name: str = None) -> None:
        """
        Initialize an Animal with a given name and image.
        
        Preconditions:
            - animal_name must be an instance of AnimalName.
            - If image_name is not provided, it defaults to the animal's enum value.
        """
        assert animal_name is not None, "Precondition failed: 'animal_name' cannot be None."
        image = f'animals/{image_name or animal_name.value}'
        super().__init__(image)
        self.animal_name: AnimalName = animal_name

    def player_entered(self, player: Player) -> list[Message]:
        """
        Handle a player stepping on the animal's pressure plate.
        
        Preconditions:
            - The 'player' argument must not be None.
            - If the player has an attribute 'is_hunter', they can't collect animals.
            - The player's current room (from get_current_room) has the remove_from_grid.

        Postconditions:
            - Updates the game state by collecting the animal.
            - Removes the animal from the grid.
            - Appends the animal to the player's inventory.
            - Returns a list containing a ChatMessage about the rescue.

        :return: A list of Message objects indicating the outcome.
        """
        assert player is not None
        assert hasattr(player, "get_current_room")
        if hasattr(player, "is_hunter"): return []
        gsm = GameStateManager()
        gsm.collect_animal()

        coord = self.get_position()
        gsm.track_picked_item(self, coord)

        room = player.get_current_room()
        assert hasattr(room, "remove_from_grid")
        room.remove_from_grid(self, self.get_position())

        if not hasattr(player, "inventory"):
            player.inventory = []
        player.inventory.append(self)


        return [ChatMessage(StaticSender("UPDATE"), room, f"You rescued a {self.animal_name.value}! ({gsm.collected_animals}/{gsm.total_animals})")]
    
class Cow(Animal):
    def __init__(self):
        super().__init__(AnimalName.COW)

class Monkey(Animal):
    def __init__(self):
        super().__init__(AnimalName.MONKEY)

class Owl(Animal):
    def __init__(self):
        super().__init__(AnimalName.OWL)

class Rabbit(Animal):
    def __init__(self):
        super().__init__(AnimalName.RABBIT)
