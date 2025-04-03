
from .imports import *
import math
import random
from typing import Literal
from .GameStateManager import GameStateManager
from .Animal import Cow, Monkey, Owl, Rabbit
from .Flower import Daisy, Orchid, Daffodil, Tulip
from .MovementStrategy import RandomMovement
from .commands import JumpCommand
from collections.abc import Callable
from .commands import JumpCommand
from .Hunter import Hunter
from .utils import StaticSender

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from NPC import NPC
    
class ScorePressurePlate(PressurePlate):
    def __init__(self, image_name='pressure_plate'):
        super().__init__(image_name)

    def player_entered(self, player) -> list[Message]:
        """ Prevents the player from interacting after game over. """
        game_state_manager = GameStateManager()  # Singleton instance
        
        # If game is over, prevent movement or interaction
        if game_state_manager.is_game_over():
            print("GAME OVER! Player cannot interact anymore.")
            return []  # Return an empty message list to block actions

        messages = super().player_entered(player)

        # Add score to player
        player.set_state("score", player.get_state("score") + 1)
        return messages

# -------------------------------------- BACKGROUND -----------------------------------------------------------------
class Tree(MapObject): 
    def __init__(self, image_name: str = 'tree_heart'):
        super().__init__(f"tile/background/{image_name}", passable=False)

# -------------------------------------- ROCKS -----------------------------------------------------------------
class Rock(PressurePlate):
    def __init__(self, image_name='rock'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Rock."""
        if hasattr(player, "is_hunter"): return []
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("rock")  # Notify game state
        
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())  
        
        return [ChatMessage(StaticSender("UPDATE"), room, f"You stepped on a rock! The hunter speeds up...")]

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

    def _get_keybinds(self) -> dict[str, Callable[["HumanPlayer"], list["Message"]]]:
        keybinds = super()._get_keybinds()  # keep built-in ones if needed

        def move_with_direction(direction: str):
            return lambda player: self._remember_and_move(player, direction)

        keybinds.update({
            "up": move_with_direction("up"),
            "down": move_with_direction("down"),
            "left": move_with_direction("left"),
            "right": move_with_direction("right"),
            "j": lambda player: JumpCommand().execute(player),  # jump still works
        })

        return keybinds

    def _remember_and_move(self, player: "HumanPlayer", direction: str) -> list["Message"]:
        player.set_state("last_direction", direction)
        return player.move(direction)
  
    def add_player(self, player: "Player", entry_point=None) -> None:
        super().add_player(player, entry_point)
        self.player_instance = player
        print(f"Player {player.get_name()} has entered the map.")
        
    def update(self) -> list[Message]:
        messages = []
        objects = getattr(self, '_Map__objects', [])
        for obj in list(objects):  # iterate over a copy
            messages.extend(obj.update())
        return messages
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        # Crearte a list of reserved positions to avoid overlapping objects
        reserved_positions = set()

        #adding trees
        tree = Tree() 
        for i in range(14):
            for pos in [Coord(0, i), Coord(14, i), Coord(i, 0), Coord(i, 14)]:
                objects.append((tree, pos))
                reserved_positions.add(pos.to_tuple())
        objects.append((tree, Coord(14, 14)))
        reserved_positions.add(Coord(14, 14).to_tuple())

        # Remove trees for the entrance
        objects.remove((tree, Coord(14,7)))
        objects.remove((tree, Coord(14,8)))
        # Remove trees for the exit
        objects.remove((tree, Coord(0,4)))
        objects.remove((tree, Coord(0,5)))

        # add a door(entrance)
        entrydoor = Door('int_entrance', linked_room="Trottier Town")
        objects.append((entrydoor, Coord(14, 7)))
        # add a door(exit)
        #TODO this actually needs to be trottier town as well but it doesnt work right now, look into it!
        exitdoor = Door('int_entrance', linked_room="Test House") 
        objects.append((exitdoor, Coord(0, 4)))

        all_positions = [Coord(x, y).to_tuple() for x in range(15) for y in range(15)]
        free_positions = set(all_positions) - reserved_positions

        # print(free_positions)

        # add rocks
        for _ in range(5):
            rock = Rock()
            pos = random.choice(list(free_positions))
            objects.append((rock, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        
        # add flowers
        for _ in range(5):
            flower = random.choice([Daisy(), Orchid(), Daffodil(), Tulip()])
            pos = random.choice(list(free_positions))
            objects.append((flower, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # add cows
        for _ in range(3):
            cow = Cow()
            pos = random.choice(list(free_positions))
            objects.append((cow, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # add monkeys
        for _ in range(3):
            monkey = Monkey()
            pos = random.choice(list(free_positions))
            objects.append((monkey, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        
        # add owls
        for _ in range(3):
            owl = Owl()
            pos = random.choice(list(free_positions))
            objects.append((owl, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # add rabbits
        for _ in range(3):
            rabbit = Rabbit()
            pos = random.choice(list(free_positions))
            objects.append((rabbit, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        
        # add the npc
        hunter = Hunter( #todo
            encounter_text="I caught you!",
            staring_distance=1,
        )
        objects.append((hunter, Coord(3,8)))

        # add a pressure plate
        pressure_plate = ScorePressurePlate('grass')
        objects.append((pressure_plate, Coord(13, 7)))

        return objects
