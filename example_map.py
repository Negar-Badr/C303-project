
from .imports import *
import math
import random
from typing import Literal
from .GameStateManager import GameStateManager
from .Animal import Cow, Monkey, Owl, Rabbit
from .Flower import Daisy, Orchid, Daffodil, Tulip
from .MovementStrategy import RandomMovement
from collections.abc import Callable
from .commands import *
from .Hunter import Hunter
from .utils import StaticSender
import copy
from .Observer import Observer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    
# -------------------------------------- DOOR ----------------------------------------------------------------- 
class LockableDoor(Door, Observer):
    def __init__(self, image_name: str, linked_room: str = "", is_main_entrance=True) -> None:
        super().__init__(image_name, linked_room, is_main_entrance)
        self._locked = False  
        self.set_passability = True  

    def lock(self):
        self._locked = True
        self.set_passability = False  

    def unlock(self):
        self._locked = False
        self.set_passability = True  
        
    def on_notify(self, subject, event):
        if event in ["WIN", "LOSE"]:
            self.unlock()

    def player_entered(self, player) -> list[Message]:
        if self._locked:
            self.set_passability = False  
            return [ChatMessage(StaticSender("SYSTEM"), player, 
                                "Uh oh... The door is locked until all animals are rescued [Evil Laugh]")]
        self.set_passability = True
        return super().player_entered(player)

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
        
        coord = self.get_position()
        game_state_manager.track_picked_item(self, coord)

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position()) 

        if not hasattr(player, "inventory"):
            player.inventory = []
        player.inventory.append(self)

                
        return [ChatMessage(StaticSender("UPDATE"), room, f"You stepped on a rock! The hunter speeds up...")]
    
# ------------------------------------ GAME INSTRUCTIONS ---------------------------------------------------------------   
class EntranceMenuPressurePlate(PressurePlate):
    def player_entered(self, player) -> list[Message]:
        room = player.get_current_room()
        if hasattr(room, "entrance_door"):
            room.entrance_door.lock()
        room.remove_from_grid(self, self.get_position())
        command = ShowIntroCommand(self)
        return command.execute(player)
    def select_option(self, player, option):
        # Do nothing, or close the menu
        return []

# -------------------------------------- OUR HOUSE -----------------------------------------------------------------
class ExampleHouse(Map):
    MAIN_ENTRANCE = True
    def __init__(self) -> None:
        super().__init__(
            name="Test House",
            description="Welcome to Paws Peril House! Please help us save the animals",
            size=(15, 15), #size of the area in the example house  
            entry_point=Coord(14, 7),
            background_tile_image='grass',
            background_music='funsong',
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
            "z": lambda player: UndoCommand().execute(player),
            "r": lambda player: ResetCommand().execute(player),
            "p": lambda player: PlayCommand().execute(player),
        })

        return keybinds

    def _remember_and_move(self, player: "HumanPlayer", direction: str) -> list["Message"]:
        player.set_state("last_direction", direction)
        return player.move(direction)
  
    def add_player(self, player: "Player", entry_point=None) -> None:
        super().add_player(player, entry_point)
        self.player_instance = player
        print(f"Player {player.get_name()} has entered the map.")
        GameStateManager().current_map = self
        
    def update(self) -> list[Message]:
        messages = []
        objects = getattr(self, '_Map__objects', [])
        for obj in list(objects):  # iterate over a copy
            messages.extend(obj.update())
        return messages
    
    def generate_items(self) -> list[tuple[MapObject, Coord]]:
        """
        Generates trees, rocks, flowers, and animals (including the NPC hunter)
        and returns them as a list of (MapObject, Coord) tuples.
        """
        objects: list[tuple[MapObject, Coord]] = []

        # Create a set to reserve positions and avoid overlaps
        reserved_positions = set()

        # --- Add Trees along the edges ---
        tree = Tree() 
        for i in range(14):
            for pos in [Coord(0, i), Coord(14, i), Coord(i, 0), Coord(i, 14)]:
                objects.append((tree, pos))
                reserved_positions.add(pos.to_tuple())
        objects.append((tree, Coord(14, 14)))
        reserved_positions.add(Coord(14, 14).to_tuple())

        # Reserve a 3x3 area around the door (door is at (14,7))
        door_zone = [(x, y) for y in range(12, 15) for x in range(6, 9)]
        for pos in door_zone:
            reserved_positions.add(pos)

        # Remove trees that conflict with the future entrance door
        objects.remove((tree, Coord(14, 7)))
        objects.remove((tree, Coord(14, 8)))

        # Determine all possible positions on the map (15x15 grid) and then calculate free positions
        all_positions = [Coord(x, y).to_tuple() for x in range(15) for y in range(15)]
        free_positions = set(all_positions) - reserved_positions

        # --- Add additional trees randomly ---
        for _ in range(50):
            new_tree = Tree()
            pos = random.choice(list(free_positions))
            objects.append((new_tree, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # --- Add Rocks ---
        for _ in range(5):
            rock = Rock()
            pos = random.choice(list(free_positions))
            objects.append((rock, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        
        # --- Add Flowers ---
        for _ in range(5):
            flower = random.choice([Daisy(), Orchid(), Daffodil(), Tulip()])
            pos = random.choice(list(free_positions))
            objects.append((flower, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # --- Add Animals ---
        # Add cows
        for _ in range(3):
            cow = Cow()
            pos = random.choice(list(free_positions))
            objects.append((cow, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        # Add monkeys
        for _ in range(3):
            monkey = Monkey()
            pos = random.choice(list(free_positions))
            objects.append((monkey, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        # Add owls
        for _ in range(3):
            owl = Owl()
            pos = random.choice(list(free_positions))
            objects.append((owl, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        # Add rabbits
        for _ in range(3):
            rabbit = Rabbit()
            pos = random.choice(list(free_positions))
            objects.append((rabbit, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # --- Add the Welcome Pressure Plate ---
        entrance_plate = EntranceMenuPressurePlate('grass')
        objects.append((entrance_plate, Coord(13, 7)))

        return objects

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        """
        Retrieves all map objects by generating the common items (trees, animals, rocks, flowers)
        and then adding the entrance door and welcome pressure plate.
        """
        objects = self.generate_items()

        # --- Add the NPC Hunter ---
        hunter = Hunter( #todo
            encounter_text="I caught you!",
            staring_distance=1,
        )
        objects.append((hunter, Coord(3,8)))

        # --- Add the Entrance Door ---
        door = LockableDoor(
            'int_entrance',
            linked_room="Trottier Town",
            is_main_entrance=True
        )
        door.unlock()  # ensure the door starts unlocked
        self.entrance_door = door  # store reference for later locking/unlocking
        objects.append((door, Coord(14, 7)))

        # Optionally store the original state of objects
        GameStateManager().store_original_objects(objects)
        if not hasattr(self, "_original_objects"):
            self._original_objects = copy.deepcopy(objects)
            
        gsm = GameStateManager()
        for obj, _ in objects:
            # Check if the object is an observer.
            if isinstance(obj, Observer):
                gsm.add_observer(obj)

        return objects

    def reset_objects(self):
        gsm = GameStateManager()

        # Step 1: Remove objects that aren't Player or Hunter
        for obj in list(getattr(self, '_Map__objects', set())):
            if not isinstance(obj, (Player, Hunter)):
                self.remove_from_grid(obj, obj.get_position())

        # Step 2: Generate new items using generate_items()
        new_items = self.generate_items()
        self._active_objects = []
        for obj, coord in new_items:
            # Create a fresh copy of the object
            new_obj = copy.deepcopy(obj)
            new_obj.set_position(coord)
            new_obj._current_room = self
            self.add_to_grid(new_obj, coord)
            self._active_objects.append((new_obj, coord))

        # Step 3: Update the existing Hunter’s movement strategy
        for obj in getattr(self, '_Map__objects', set()):
            if isinstance(obj, Hunter):
                obj.movement_strategy = RandomMovement()
                print("🐾 Hunter strategy reset to", type(obj.movement_strategy).__name__)

        # --- Add the Entrance Door ---
        door = LockableDoor(
            'int_entrance',
            linked_room="Trottier Town",
            is_main_entrance=True
        )
        door.unlock()  # ensure the door starts unlocked
        self.entrance_door = door  # store reference for later locking/unlocking
        self.add_to_grid(door, Coord(14, 7))
        gsm.add_observer(door)  # Add the door as an observer

