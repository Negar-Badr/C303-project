from .imports import *
import random
from .GameStateManager import *
from .Animal import Cow, Monkey, Owl, Rabbit
from .Flower import *
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
    def __init__(self, image_name: str, linked_room: str = "", is_main_entrance: bool = True) -> None:
        """
        Initialize the LockableDoor.

        Preconditions:
          - image_name is a non-empty string.
          - linked_room is a string (can be empty).
          - is_main_entrance is a boolean.
        Postconditions:
          - self._locked is set to False.
          - self.set_passability is set to True.
        """
        assert isinstance(image_name, str) and image_name, "image_name must be a non-empty string."
        super().__init__(image_name, linked_room, is_main_entrance)
        self._locked: bool = False  
        self.set_passability: bool = True  

    def lock(self) -> None:
        """Lock the door."""
        self._locked = True
        self.set_passability = False  

    def unlock(self) -> None:
        """Unlock the door."""
        self._locked = False
        self.set_passability = True  
        
    def on_notify(self, event: str) -> None:
        """
        React to notifications.

        Preconditions:
          - event must be a non-empty string.
        Postconditions:
          - If event is "WIN" or "LOSE", the door is unlocked.
        """
        assert isinstance(event, str) and event, "event must be a non-empty string."
        if event in ["WIN", "LOSE"]:
            self.unlock()

    def player_entered(self, player: Player) -> List["Message"]:
        """
        Handle a player entering the door.

        Preconditions:
          - player is a valid object that supports the methods used below.
        Postconditions:
          - If the door is locked, it returns a ChatMessage alerting the player.
          - Otherwise, it delegates to the superclass method.
        """
        if self._locked:
            self.set_passability = False  
            return [ChatMessage(StaticSender("SYSTEM"), player, 
                                "Uh oh... The door is locked until all animals are rescued [Evil Laugh]")]
        self.set_passability = True
        return super().player_entered(player)

# -------------------------------------- BACKGROUND -----------------------------------------------------------------
class Tree(MapObject): 
    def __init__(self, image_name: str = 'tree_heart') -> None:
        """
        Initialize a Tree object.

        Preconditions:
          - image_name must be a non-empty string.
        Postconditions:
          - The object is initialized with the image at "tile/background/{image_name}".
          - The object is set as not passable.
        """
        assert isinstance(image_name, str) and image_name, "image_name must be a non-empty string."
        super().__init__(f"tile/background/{image_name}", passable=False)

# -------------------------------------- ROCKS -----------------------------------------------------------------
class Rock(PressurePlate):
    """A rock that the player can step on, triggering state changes."""
   
    def __init__(self, image_name: str = 'rock') -> None:
        """
        Initialize a Rock object.

        Preconditions:
          - image_name is a non-empty string.
        Postconditions:
          - The Rock is initialized with the specified image.
        """
        assert isinstance(image_name, str) and image_name, "image_name must be a non-empty string."
        super().__init__(image_name)
        
    def player_entered(self, player: Player) -> List["Message"]:
        """
        Handle the player stepping on the rock.

        Preconditions:
          - player is a valid object that provides get_current_room() and an attribute inventory.
        Postconditions:
          - The rock is collected by the game state manager.
          - The player's inventory is updated.
          - A ChatMessage is returned describing the event.
        """
        if hasattr(player, "is_hunter"):
            return []
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
    """A pressure plate that triggers game instructions when the player enters."""
    
    def player_entered(self, player: Player) -> List["Message"]:
        """
        Handle the player stepping on the entrance menu pressure plate.

        Preconditions:
          - player is a valid object that may support a method named set_current_menu.
        Postconditions:
          - The door is locked (if applicable) and the pressure plate is removed from the grid.
          - The ShowIntroCommand is executed for the player.
        """
        if not hasattr(player, "set_current_menu"):
            return [] 
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
    """
    A concrete map representing an example house with game instructions, items, and NPCs.
    
    Invariants:
      - The map has a defined size (15x15).
      - The entrance is located at Coord(14, 7).
    """
    MAIN_ENTRANCE: bool = True

    def __init__(self) -> None:
        """
        Initialize the ExampleHouse.

        Postconditions:
          - The house is initialized with a name, description, size, entry point, background tile, and background music.
        """
        super().__init__(
            name="Test House",
            description="Welcome to Paws Peril House! Please help us save the animals",
            size=(15, 15), #size of the area in the example house  
            entry_point=Coord(14, 7),
            background_tile_image='grass',
            background_music='funsong',
        )

    def _get_keybinds(self) -> dict[str, Callable[["HumanPlayer"], List["Message"]]]:
        """
        Retrieve the key bindings for player actions within the house.

        Postconditions:
          - Returns a dictionary mapping keys to functions that take a HumanPlayer and return a list of Message.
        """
        keybinds = super()._get_keybinds()  # keep built-in ones if needed

        def move_with_direction(direction: str) -> Callable[["HumanPlayer"], List["Message"]]:
            return lambda player: self._remember_and_move(player, direction)

        keybinds.update({
            "up": move_with_direction("up"),
            "down": move_with_direction("down"),
            "left": move_with_direction("left"),
            "right": move_with_direction("right"),
            "j": lambda player: JumpCommand().execute(player),  # jump still works
            "z": lambda player: UndoCommand().execute(player),
            "r": lambda player: ResetCommand().execute(player),  # to reset 
            "p": lambda player: ResetCommand().execute(player),  # to play 
        })

        return keybinds

    def _remember_and_move(self, player: "HumanPlayer", direction: str) -> List["Message"]:
        """
        Remembers the last direction moved by the player and initiates movement.

        Preconditions:
          - direction is a non-empty string.
          - player supports set_state and move methods.
        Postconditions:
          - The player's last direction is recorded.
          - The player's move command is executed and returns a list of Messages.
        """
        assert isinstance(direction, str) and direction, "direction must be a non-empty string."
        player.set_state("last_direction", direction)
        return player.move(direction)
  
    def add_player(self, player: "Player", entry_point: Optional["Coord"] = None) -> None:
        """
        Add a player to the map at the specified entry point.

        Preconditions:
          - player is a valid Player.
          - entry_point is either None or a valid Coord.
        Postconditions:
          - The player is added to the map.
          - The map’s player_instance is set.
          - The GameStateManager's current_map is updated.
        """
        super().add_player(player, entry_point)
        self.player_instance = player
        print(f"Player {player.get_name()} has entered the map.")
        GameStateManager().current_map = self
        
    def update(self) -> List["Message"]:
        """
        Update all objects on the map.

        Postconditions:
          - Returns a list of Messages produced by updating each map object.
        """
        messages: List["Message"] = []
        objects = getattr(self, '_Map__objects', [])
        for obj in list(objects):  # iterate over a copy to avoid modification during iteration
            messages.extend(obj.update())
        return messages
    
    def generate_items(self) -> List[Tuple["MapObject", "Coord"]]:
        """
        Generates trees, rocks, flowers, and animals (including the NPC hunter)
        and returns them as a list of (MapObject, Coord) tuples.

        Postconditions:
          - Returns a list of generated items without overlapping positions.
        """
        objects: List[Tuple["MapObject", "Coord"]] = []

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

        # Remove trees that conflict with the future entrance door.
        objects.remove((tree, Coord(14, 7)))
        objects.remove((tree, Coord(14, 8)))

        # Determine all possible positions on the map (15x15 grid) and then calculate free positions.
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

    def get_objects(self) -> List[Tuple["MapObject", "Coord"]]:
        """
        Retrieves all map objects by generating common items and then adding special objects like the hunter and door.

        Postconditions:
          - Returns a list of (MapObject, Coord) tuples.
          - Registers observers for objects that implement Observer.
        """
        objects = self.generate_items()

        # --- Add the NPC Hunter ---
        hunter = Hunter( 
            encounter_text="I caught you!",
            staring_distance=1,
        )
        objects.append((hunter, Coord(3, 8)))

        # --- Add the Entrance Door ---
        door = LockableDoor(
            'int_entrance',
            linked_room="Trottier Town",
            is_main_entrance=True
        )
        door.unlock()  # Ensure the door starts unlocked.
        self.entrance_door = door  # Store reference for later locking/unlocking.
        objects.append((door, Coord(14, 7)))

        GameStateManager().store_original_objects(objects)
        if not hasattr(self, "_original_objects"):
            self._original_objects = copy.deepcopy(objects)
            
        gsm = GameStateManager()
        for obj, _ in objects:
            if isinstance(obj, Observer):
                gsm.add_observer(obj)

        return objects

    def reset_objects(self) -> None:
        """
        Reset objects contributing to the map while preserving essential ones such as Player, Hunter, and the main door.

        Postconditions:
          - New objects are generated, added to the grid, and stored.
        """
        gsm = GameStateManager()

        # Step 1: Remove objects that aren't Player, Hunter, or LockableDoor
        for obj in list(getattr(self, '_Map__objects', set())):
            if not isinstance(obj, (Player, Hunter, LockableDoor)):
                self.remove_from_grid(obj, obj.get_position())

        # Step 2: Generate new items using generate_items()
        new_items = self.generate_items()
        self._active_objects = []
        for obj, coord in new_items:
            # Create a fresh copy of the object.
            new_obj = copy.deepcopy(obj)
            new_obj.set_position(coord)
            new_obj._current_room = self
            self.add_to_grid(new_obj, coord)
            self._active_objects.append((new_obj, coord))