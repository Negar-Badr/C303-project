
from .imports import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *

class ScorePressurePlate(PressurePlate):
    def __init__(self, image_name='pressure_plate'):
        super().__init__(image_name)
    
    def player_entered(self, player) -> list[Message]:
        messages = super().player_entered(player)

        # add score to player
        player.set_state("score", player.get_state("score") + 1)

        return messages
    
class Tree(MapObject): 
    def __init__(self, image_name: str = "tree_heart"):
        super().__init__(f"tile/background/{image_name}", passable=True)

class Cow(PressurePlate):
    def __init__(self, image_name='cow'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

class ExampleHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Test House",
            description="Welcome",
            size=(50, 50),
            entry_point=Coord(14, 7),
            background_tile_image='grass',
        )
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        #add tree (temporary, make it better later)
        tree = Tree() 
        objects.append((tree, Coord(0,2)))

        tree = Tree() 
        objects.append((tree, Coord(0,4)))

        tree = Tree() 
        objects.append((tree, Coord(0,6)))

        tree = Tree() 
        objects.append((tree, Coord(0,8)))

        tree = Tree() 
        objects.append((tree, Coord(0,10)))

        tree = Tree() 
        objects.append((tree, Coord(0,12)))

        tree = Tree() 
        objects.append((tree, Coord(0,14)))

        tree = Tree() 
        objects.append((tree, Coord(0,16)))

        tree = Tree() 
        objects.append((tree, Coord(0,18)))

        tree = Tree() 
        objects.append((tree, Coord(2,18)))

        tree = Tree() 
        objects.append((tree, Coord(4,18)))

        tree = Tree() 
        objects.append((tree, Coord(6,18)))

        tree = Tree() 
        objects.append((tree, Coord(8,18)))

        tree = Tree() 
        objects.append((tree, Coord(10,18)))

        tree = Tree() 
        objects.append((tree, Coord(12,18)))

        tree = Tree() 
        objects.append((tree, Coord(2,2)))

        tree = Tree() 
        objects.append((tree, Coord(4,2)))

        tree = Tree() 
        objects.append((tree, Coord(6,2)))

        tree = Tree() 
        objects.append((tree, Coord(8,2)))

        tree = Tree() 
        objects.append((tree, Coord(10,2)))

        tree = Tree() 
        objects.append((tree, Coord(12,2)))

        tree = Tree() 
        objects.append((tree, Coord(12,4)))

        tree = Tree() 
        objects.append((tree, Coord(12,6)))

        tree = Tree() 
        objects.append((tree, Coord(12,8)))

        tree = Tree() 
        objects.append((tree, Coord(12,12)))

        tree = Tree() 
        objects.append((tree, Coord(12,14)))

        tree = Tree() 
        objects.append((tree, Coord(12,16)))

        tree = Tree() 
        objects.append((tree, Coord(12,18)))


        #add cows 
        cow = Cow()
        objects.append((cow, Coord(5, 5)))

        cow = Cow()
        objects.append((cow, Coord(8, 7)))

        # add a door
        door = Door('int_entrance', linked_room="Trottier Town")
        objects.append((door, Coord(14, 10)))

        # add a pressure plate
        # pressure_plate = ScorePressurePlate()
        # objects.append((pressure_plate, Coord(13, 7)))

        return objects


class PawsPerilHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Paws in Peril House",
            description="Welcome to Paws in Peril House!",
            size=(15, 15),
            entry_point=Coord(14, 7),
            background_tile_image='cobblestone',
        )
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        # add a door
        door = Door('int_entrance', linked_room="Trottier Town")
        objects.append((door, Coord(14, 7)))

        # add a pressure plate
        pressure_plate = ScorePressurePlate()
        objects.append((pressure_plate, Coord(13, 7)))

        return objects
