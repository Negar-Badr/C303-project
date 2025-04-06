
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

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    
# -------------------------------------- DOOR ----------------------------------------------------------------- 
class LockableDoor(Door):
    def __init__(self, image_name: str, linked_room: str = "", is_main_entrance=False, original_connected_room=None, original_entry_point=None) -> None:
        super().__init__(image_name, linked_room, is_main_entrance)
        self._locked = False  

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def player_entered(self, player) -> list[Message]:
        if self._locked:
            return [ChatMessage(StaticSender("SYSTEM"), player, "Uh oh... The door is locked until all animals are rescued [Evil Laugh]")]
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

# -------------------------------------- OUR HOUSE -----------------------------------------------------------------
class ExampleHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Test House",
            description="Welcome to Paws Peril House! Please help us save the animals",
            size=(15, 15), #size of the area in the example house  
            entry_point=Coord(14, 7),
            background_tile_image='grass',
            background_music='pawsperil',
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

         # Reserve a 3x3 area around the door (door is at (14,7))
        door_zone = [(x, y) for y in range(12, 15) for x in range(6, 9)]
        for pos in door_zone:
            reserved_positions.add(pos)

        door = LockableDoor(
            'int_entrance',
            linked_room="Trottier Town",
            original_connected_room='int_entrance',  # or the actual map/room object if available
            original_entry_point=Coord(14, 7)           # set this to the proper entry point
        )
        door.unlock()  # ensure the door starts unlocked
        self.entrance_door = door  # store reference for later locking/unlocking
        objects.append((door, Coord(14, 7)))

        all_positions = [Coord(x, y).to_tuple() for x in range(15) for y in range(15)]
        free_positions = set(all_positions) - reserved_positions

        # Add tree clusters as obstacles
        # Decide how many clusters to add (this can be fixed or random)
        num_clusters = 17 
        for _ in range(num_clusters):
            # Randomly decide cluster size: 1 (single tree), 2, or 3
            cluster_size = random.choice([1, 2, 3])
            attempts = 0
            placed = False
            while attempts < 10 and not placed:
                start = random.choice(list(free_positions))
                cluster_coords = [start]
                if cluster_size > 1:
                    # Randomly choose an orientation: horizontal or vertical
                    orientation = random.choice(['horizontal', 'vertical'])
                    valid_cluster = True
                    # Try to add the remaining tiles in the chosen orientation
                    for i in range(1, cluster_size):
                        if orientation == 'horizontal':
                            next_coord = (start[0], start[1] + i)
                        else:
                            next_coord = (start[0] + i, start[1])
                        if next_coord not in free_positions:
                            valid_cluster = False
                            break
                        cluster_coords.append(next_coord)
                    if not valid_cluster:
                        attempts += 1
                        continue
                # If valid, add a Tree at each coordinate in the cluster
                for pos in cluster_coords:
                    objects.append((Tree(), Coord(pos[1], pos[0])))
                    free_positions.remove(pos)
                placed = True


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
        # Replace the previous pressure plate with the entrance menu pressure plate
        entrance_plate = EntranceMenuPressurePlate('grass')
        objects.append((entrance_plate, Coord(13, 7)))

        return objects
