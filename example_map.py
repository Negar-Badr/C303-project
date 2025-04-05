
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
from .commands import *
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
        
        coord = self.get_position()
        game_state_manager.track_picked_item(self, coord)

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position()) 

        if not hasattr(player, "inventory"):
            player.inventory = []
        player.inventory.append(self)

                
        return [ChatMessage(StaticSender("UPDATE"), room, f"You stepped on a rock! The hunter speeds up...")]
    
# ------------------------------------ GAME INSTRUCTIONS ---------------------------------------------------------------   
class ShowIntroCommand(Command):
    """A command that displays the introduction pop-up and menu when triggered."""
    def __init__(self, pressure_plate):
        super().__init__()
        self.__pressure_plate = pressure_plate 

    def execute(self, player) -> list["Message"]:
        player.set_current_menu(self.__pressure_plate)

        messages = []

        intro_text = (
            "Welcome to Paws in Peril!\n"
            "Save all animals and escape without getting caught by the hunter.\n"
            "You can jump using j."
        )
        tips_text = (
            "Steer clear of the rocks, and collect flowers to nullify their effect.\n"
            "Good luck!"
        )
        messages.append(
            DialogueMessage(
                sender=self.__pressure_plate, 
                recipient=player, 
                text=intro_text, 
                image="EmptyPlate",        
                bg_color=(247, 190, 211),  
                text_color=(0, 0, 0)       
            )
        )
        messages.append(
            DialogueMessage(
                sender=self.__pressure_plate, 
                recipient=player, 
                text=tips_text, 
                image="EmptyPlate",       
                bg_color=(247, 190, 211),  
                text_color=(0, 0, 0)       
            )
        )

        return messages

class EntranceMenuPressurePlate(PressurePlate):
    def player_entered(self, player) -> list[Message]:
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

        reserved_positions.add(Coord(13, 7).to_tuple())
        reserved_positions.add(Coord(13, 8).to_tuple())

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
