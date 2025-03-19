
from .imports import *
import math
import random
from typing import Literal
from .GameStateManager import GameStateManager

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
    
# -------------------------------------- BACKGROUND -----------------------------------------------------------------
class Tree(MapObject): 
    def __init__(self, image_name: str = 'tree_heart'):
        super().__init__(f"tile/background/{image_name}", passable=False)

class Left(MapObject): 
    def __init__(self, image_name: str = 'shallow_pit_left'):
        super().__init__(f"tile/background/{image_name}", passable=True)
class Right(MapObject): 
    def __init__(self, image_name: str = 'shallow_pit_right'):
        super().__init__(f"tile/background/{image_name}", passable=True)

# -------------------------------------- ANIMALS -----------------------------------------------------------------
class Cow(PressurePlate):
    def __init__(self, image_name='animals/cow'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Cow."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("cow")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return [] 
    
class Monkey(PressurePlate):
    def __init__(self, image_name='animals/monkey'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Monkey."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("monkey")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return [] 
    
class Owl(PressurePlate):
    def __init__(self, image_name='animals/owl'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Owl."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("owl")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
    
class Rabbit(PressurePlate):
    def __init__(self, image_name='animals/rabbit'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Rabbit."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("rabbit")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

# -------------------------------------- ROCKS -----------------------------------------------------------------
class Rock(PressurePlate):
    def __init__(self, image_name='rock'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Rock."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("rock")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

# -------------------------------------- FLOWERS -----------------------------------------------------------------
class Daisy(PressurePlate):
    def __init__(self, image_name='flowers/Daisy'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Daisy."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

class Orchid(PressurePlate):
    def __init__(self, image_name='flowers/Orchid'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on an Orchid."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return [] 
    
class Daffodil(PressurePlate):
    def __init__(self, image_name='flowers/Daffodil'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on an Daffodil."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
    
class Tulip(PressurePlate):
    def __init__(self, image_name='flowers/Tulip'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on an Tulip."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
  
# -------------------------------------- HUNTER -----------------------------------------------------------------
class Hunter(Professor):
    def __init__(self, encounter_text: str, staring_distance: int = 0, facing_direction: Literal['up', 'down', 'left', 'right'] ='down') -> None:
        super().__init__(
            encounter_text=encounter_text,
            facing_direction=facing_direction,
            staring_distance=staring_distance,
        )
    
    def update(self) -> list["Message"]:
        """Hunter moves based on the current strategy."""
        game_state_manager = GameStateManager()  # Singleton instance
        strategy = game_state_manager.get_hunter_strategy()

        # TODO: strategy 
        if strategy == "teleportation":
            # Simulate teleportation movement (random position)
            new_x, new_y = random.randint(0, 14), random.randint(0, 19)
            print(f"Hunter teleports to {new_x}, {new_y}")
            return self.move_to(Coord(new_x, new_y))  # Assuming move_to is implemented
        
        elif strategy == "shortest-path":
            # Implement pathfinding logic (A* or BFS)
            print("Hunter moves towards the player using shortest path.")
            return self.move_toward_player()  # Assuming move_toward_player() is implemented
        
        else:
            # Default movement (random)
            direction: Literal["up", "down", "left", "right"] = random.choice(['up', 'down', 'left', 'right'])
            print(f"Hunter moves randomly: {direction}")
            return self.move(direction) 
  




# -------------------------------------- OUR HOUSE -----------------------------------------------------------------
class ExampleHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Test House",
            description="Welcome to Paws Peril House! Please help us save the animals",
            size=(15, 15), #size of the area in the example house  
            entry_point=Coord(14, 7),
            background_tile_image='grass',
            background_music='blithe', #todo
        )
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        #adding trees
        tree = Tree() 
        for i in range(14):
            objects.append((tree, Coord(0,i)))
            objects.append((tree, Coord(14,i)))
            objects.append((tree, Coord(i,0)))
            objects.append((tree, Coord(i,14)))
        objects.append((tree, Coord(14,14)))

        # Remove trees for the entrance
        objects.remove((tree, Coord(14,7)))
        objects.remove((tree, Coord(14,8)))
        # Remove trees for the exit
        objects.remove((tree, Coord(0,4)))
        objects.remove((tree, Coord(0,5)))

        # add a door(entrance)
        door = Door('int_entrance', linked_room="Trottier Town")
        objects.append((door, Coord(14, 7)))
        # add a door(exit)
        door = Door('int_entrance', linked_room="Paws in Peril House")
        objects.append((door, Coord(0, 4)))

        # add rocks
        rock = Rock()
        objects.append((rock, Coord(8, 1)))
        rock = Rock()
        objects.append((rock, Coord(6,5)))

        # add flowers
        daisy = Daisy()
        objects.append((daisy, Coord(9, 13)))
        orchid = Orchid()
        objects.append((orchid, Coord(9, 10)))
        daffodil = Daffodil()
        objects.append((daffodil, Coord(9, 5)))
        tulip = Tulip()
        objects.append((tulip, Coord(9, 11)))

        #add cows 
        cow = Cow()
        objects.append((cow, Coord(5, 5)))
        cow = Cow()
        objects.append((cow, Coord(8, 7)))
        cow = Cow()
        objects.append((cow, Coord(7, 2)))
        cow = Cow()
        objects.append((cow, Coord(4, 3)))

        #add monkeys
        monkey = Monkey()
        objects.append((monkey, Coord(3, 5)))
        monkey = Monkey()
        objects.append((monkey, Coord(2, 7)))
        monkey = Monkey()
        objects.append((monkey, Coord(1, 2)))

        #add owls
        owl = Owl()
        objects.append((owl, Coord(4, 7)))
        owl = Owl()
        objects.append((owl, Coord(2, 3)))
        owl = Owl()
        objects.append((owl, Coord(1, 7)))

        #add rabbits
        rabbit = Rabbit()
        objects.append((rabbit, Coord(5, 7)))
        rabbit = Rabbit()
        objects.append((rabbit, Coord(6, 3)))
        rabbit = Rabbit()
        objects.append((rabbit, Coord(7, 7)))

        # add the npc
        hunter = Hunter( #todo
            encounter_text="I will hunt you down",
            staring_distance=1,
        )
        objects.append((hunter, Coord(3,8)))

        # add a pressure plate
        # pressure_plate = ScorePressurePlate()
        # objects.append((pressure_plate, Coord(13, 7)))

        return objects
