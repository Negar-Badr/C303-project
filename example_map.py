
from .imports import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from ..NPC import Professor, WalkingProfessor, NPC

class ScorePressurePlate(PressurePlate):
    def __init__(self, image_name='pressure_plate'):
        super().__init__(image_name)
    
    def player_entered(self, player) -> list[Message]:
        messages = super().player_entered(player)

        # add score to player
        player.set_state("score", player.get_state("score") + 1)

        return messages
    
class Tree(MapObject): 
    def __init__(self, image_name: str = 'tree_heart'):
        super().__init__(f"tile/background/{image_name}", passable=True)

class Left(MapObject): 
    def __init__(self, image_name: str = 'shallow_pit_left'):
        super().__init__(f"tile/background/{image_name}", passable=True)
class Right(MapObject): 
    def __init__(self, image_name: str = 'shallow_pit_right'):
        super().__init__(f"tile/background/{image_name}", passable=True)

class Cow(PressurePlate):
    def __init__(self, image_name='cow'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []


class Rock(PressurePlate):
    def __init__(self, image_name='rock'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

class Daisy(PressurePlate):
    def __init__(self, image_name='Daisy'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
    
class Orchid(PressurePlate):
    def __init__(self, image_name='Orchid'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
    
class ExampleHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Test House",
            description="Welcome to Paws Peril House! Please help us save the animals",
            size=(50, 50),
            entry_point=Coord(14, 7),
            background_tile_image='grass',
            background_music='blithe', #todo
        )
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        #adding trees
        tree = Tree() 
        objects.append((tree, Coord(20,22)))
        objects.append((tree, Coord(20,24)))
        objects.append((tree, Coord(20,26)))
        objects.append((tree, Coord(20,28)))
        objects.append((tree, Coord(20,30)))
        objects.append((tree, Coord(20,32)))     
        objects.append((tree, Coord(20,34)))
        objects.append((tree, Coord(20,36)))
        objects.append((tree, Coord(20,38)))

        objects.append((tree, Coord(22,38))) 
        objects.append((tree, Coord(24,38)))
        objects.append((tree, Coord(26,38)))
        objects.append((tree, Coord(28,38)))
        objects.append((tree, Coord(30,38)))
        objects.append((tree, Coord(32,38)))

        objects.append((tree, Coord(22,22)))
        objects.append((tree, Coord(24,22)))
        objects.append((tree, Coord(26,22)))
        objects.append((tree, Coord(28,22)))
        objects.append((tree, Coord(30,22)))
        objects.append((tree, Coord(32,22)))

        objects.append((tree, Coord(32,24)))
        objects.append((tree, Coord(32,26)))
        objects.append((tree, Coord(32,28)))
        objects.append((tree, Coord(32,32)))
        objects.append((tree, Coord(32,34)))
        objects.append((tree, Coord(32,36)))

        # add rocks
        rock = Rock()
        objects.append((rock, Coord(28, 33)))
        rock = Rock()
        objects.append((rock, Coord(26,25)))

        # add flowers
        daisy = Daisy()
        objects.append((daisy, Coord(29, 33)))
        orchid = Orchid()
        objects.append((orchid, Coord(29, 26)))

        #add cows 
        cow = Cow()
        objects.append((cow, Coord(25, 25)))
        cow = Cow()
        objects.append((cow, Coord(28, 27)))
        cow = Cow()
        objects.append((cow, Coord(27, 35)))
        cow = Cow()
        objects.append((cow, Coord(24, 33)))

        # add the npc
        hunter = WalkingProfessor( #todo
            encounter_text="I will hunt you down",
            staring_distance=1,
        )
        objects.append((hunter, Coord(23,28)))

        # add a door
        door = Door('int_entrance', linked_room="Trottier Town")
        objects.append((door, Coord(38, 30)))

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
