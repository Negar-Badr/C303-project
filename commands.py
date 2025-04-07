from abc import ABC, abstractmethod
from .imports import *
from .GameStateManager import GameStateManager
from typing import TYPE_CHECKING
from .MovementStrategy import RandomMovement
from .example_map import ExampleHouse

if TYPE_CHECKING:
    from coord import Coord

class Command(ABC):
    @abstractmethod
    def execute(self, player: "HumanPlayer") -> list["Message"]:
        pass

class JumpCommand(Command):
    def execute(self, player: "HumanPlayer") -> list["Message"]:
        direction = player.get_facing_direction()
        if not direction:
            return []

        dy, dx = {             # bcz they are flipped
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }[direction]

        current_pos = player.get_current_position()
        room = player.get_current_room()
        jumped_pose = current_pos + Coord(2 * dx, 2 * dy)

        # Check bounds
        if not (1 <= jumped_pose.x < 14 and 1 <= jumped_pose.y < 14):
            return []

        # Check passability
        target_objs = room.get_map_objects_at(jumped_pose)
        for obj in target_objs:
            # If any object is not passable, don't jump.
            if not obj.is_passable():
                return []
    
        # Set the postions of the player
        room.remove_player(player)
        player.set_position(jumped_pose)  
        room.add_player(player, jumped_pose)

        messages = []

        # Iterate over objects on the tile and trigger pressure plates
        # this is bcz undo command lets object stack on top of each other
        for obj in room.get_map_objects_at(jumped_pose):
            if isinstance(obj, PressurePlate):
                messages.extend(obj.player_entered(player))
        
        # update the grid after the move.
        messages.append(GridMessage(player))
        return messages
    
class ResetCommand(Command):
    def execute(self, player):
        gsm = GameStateManager()
        gsm.set_game_state("playing")
        self.collected_items = []  # Stores collected items (e.g., rock, flower)
        self.collected_animals = 0  # Count of collected animals
        self.hunter_strategy = RandomMovement()
        self._initialized = True  # Mark as true at first
        self.tracked_picked_items = []  # for undo support
        self.current_map = None

        # Create a new map instance to generate a new, random layout.
        new_map = ExampleHouse()
        self.current_map = new_map

        new_map.add_player(player)

        print("its working")
        return [GridMessage(player), ChatMessage(player, player.get_current_room(), "You have reset the game.")]  # TODO: add a message for the player

class UndoCommand(Command):
    def execute(self, player):
        gsm = GameStateManager()

        if gsm.tracked_picked_items:
            _, item = gsm.tracked_picked_items.pop()

            if hasattr(player, "inventory") and item in player.inventory:
                player.inventory.remove(item)

            drop_coord = player.get_current_position()
            room = player.get_current_room()
            room.add_to_grid(item, drop_coord)

            gsm.undo_collect_item(item)

            if "animal" in str(type(item)).lower():
                msg = f"Dropped {type(item).__name__} at your current location. ({gsm.collected_animals}/{gsm.total_animals} animals rescued)"
            else:
                msg = f"Dropped {type(item).__name__} at your current location."

            return [
                ChatMessage(player, room, msg),
                GridMessage(player, send_desc=False)
            ]

        return [ChatMessage(player, player.get_current_room(), "Nothing to undo.")]
    
    
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
