from abc import ABC, abstractmethod
from .imports import *
from .GameStateManager import GameStateManager
from .utils import StaticSender
from typing import TYPE_CHECKING
from .GameStateManager import GameState


if TYPE_CHECKING:
    from coord import Coord

class Command(ABC):
    @abstractmethod
    # Execute the command for the given player.
    def execute(self, player: HumanPlayer) -> list["Message"]:
        pass

class JumpCommand(Command):
    def execute(self, player: HumanPlayer) -> list["Message"]:
        """
        Executes a jump command for the player.
        
        Preconditions:
            - player must not be None.
            - player.get_facing_direction() must return one of the following strings: "up", "down", "left", "right".
            - player.get_current_position() must return a position object that supports addition with a Coord.
            - player.get_current_room() must return a room object supporting get_map_objects_at, remove_player,
              add_player, etc.
            - The resulting jump position must be within allowed bounds (1 <= x < 14 and 1 <= y < 14).
        Postconditions:
            - The player's position is updated to the new jump position if all conditions are met.
            - The room grid is updated (old position removed and new position added).
            - PressurePlate objects at the target tile are triggered, and their messages are collected.
            - A GridMessage is appended as an update.
        
        :param player: The HumanPlayer executing the jump.
        :return: A list of Message objects indicating the outcome of the jump.
        """
        assert player is not None, "Precondition failed: 'player' cannot be None."
        assert hasattr(player, "get_facing_direction"), "Precondition failed: 'player' must have 'get_facing_direction()' method."

        direction = player.get_facing_direction()
        assert direction, "Precondition failed: 'player.get_facing_direction()' must return a valid direction."

        if not direction:
            return []

        possible_direction = {             # bcz they are flipped
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        assert direction in possible_direction, f"Precondition failed: Invalid facing direction '{direction}'."
        dy, dx = possible_direction[direction]

        # Calculate the jump position
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

        messages: list["Message"] = []

        # Iterate over objects on the tile and trigger pressure plates
        # this is bcz undo command lets object stack on top of each other
        for obj in room.get_map_objects_at(jumped_pose):
            if isinstance(obj, PressurePlate):
                messages.extend(obj.player_entered(player))
        
        # update the grid after the move.
        messages.append(GridMessage(player))
        return messages
    
       
class UndoCommand(Command):
    def execute(self, player: HumanPlayer) -> list["Message"]:
        """
        Undos the last commands for the player.
        
        Preconditions:
            - player must not be None.
            - A GameStateManager instance must have a non-empty tracked_picked_items stack if an undo is possible.
            - player must have an 'inventory' attribute if applicable.
            - player.get_current_position() and player.get_current_room() must work as expected.
        Postconditions:
            - If an item is undone:
                - It is removed from the player's inventory.
                - It is re-added to the room grid.
                - GameStateManager's item collection is updated.
                - A ChatMessage and GridMessage are returned.
            - Otherwise, a ChatMessage indicates that there is nothing to undo.
        
        :param player: The HumanPlayer executing the undo.
        :return: A list of Message objects indicating the outcome.
        """
        assert player is not None, "Precondition failed: 'player' cannot be None."
        assert hasattr(player, "get_current_position"), "Precondition failed: 'player' must have 'get_current_position()' method."
        assert hasattr(player, "inventory"), "Precondition failed: 'player' must have 'inventory' attribute."

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
                ChatMessage(StaticSender("UPDATE"), room, msg),
                GridMessage(player, send_desc=False)
            ]

        return [ChatMessage(StaticSender("UPDATE"), player.get_current_room(), "Nothing to undo.")]
    
    
class ShowIntroCommand(Command):
    """
    A command that displays the introduction pop-up and menu when triggered.
    """
    def __init__(self, pressure_plate: PressurePlate) -> None:
        """
        Initialize the ShowIntroCommand with a pressure plate.
        :param pressure_plate: The pressure plate that triggered this command.

        Preconditions:
            - pressure_plate must not be None.

        """
        super().__init__()
        assert pressure_plate is not None, "Precondition failed: 'pressure_plate' cannot be None."
        self.__pressure_plate = pressure_plate 

    def execute(self, player: HumanPlayer) -> list["Message"]:
        """
        Execute the command to display the introduction dialogue and menu.
        
        Preconditions:
            - player must not be None.
            - player has player.set_current_menu()
        Postconditions:
            - The player's current menu is updated to display the introduction.
            - Two DialogueMessages (one for intro and one for tips) are returned.
        
        :param player: The HumanPlayer to receive the introduction menu.
        :return: A list of Message objects containing the dialogue messages.
        """
        assert player is not None, "Precondition failed: 'player' cannot be None."
        assert hasattr(player, "set_current_menu"), "Precondition failed: 'player' must have 'set_current_menu()' method."

        player.set_current_menu(self.__pressure_plate)

        messages: list['Message'] = []

        intro_text = (
            "Rescue all animals!\n"
            "Avoid rocks!\n"
            "Collect flowers to stay safe:)"
        )

        tips_text = (
            "- Press 'j' to jump\n"
            "- Press 'z' to undo\n"
            "- Press 'r' to reset the map"
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
    
class ResetCommand(Command):
    """A command that resets the game"""
    from .Hunter import Hunter
    
    def execute(self, player: HumanPlayer) -> list["Message"]:
        """
        Resets the game state and map objects for the player.
        Preconditions:
            - player must not be None.
            - GameStateManager must have a valid state.
            - The current map must support reset_objects and player management.
        Postconditions:
            - The game state is reset.
            - The map objects are reset.
            - The player is re-added to the map.
            - A GridMessage and ChatMessage are returned indicating the reset status.
        :param player: The HumanPlayer executing the reset.
        :return: A list of Message objects indicating the outcome.
        """
        assert player is not None, "Precondition failed: 'player' cannot be None."

        gsm = GameStateManager()
        assert gsm is not None, "Precondition failed: 'GameStateManager' cannot be None."
        if gsm.get_state() not in [GameState.WIN, GameState.LOSE]:
            return [
                ChatMessage(StaticSender("SYSTEM"), player.get_current_room(), "You can only reset after winning or losing the game."),
            ]
        assert gsm.reset_game_state is not None, "Precondition failed: 'GameStateManager' must have a valid reset_game_state method."
        # Reset game variables
        gsm.reset_game_state()

        current_map = gsm.current_map
        if current_map and hasattr(current_map, "reset_objects"):
            current_map.reset_objects()
            current_map.remove_player(player)
            current_map.add_player(player)
            print("Map objects and player have been reset.")

            for obj, _ in current_map._active_objects:
                if isinstance(obj, self.Hunter):
                    print("Hunter strategy after reset is:", type(obj.movement_strategy).__name__)

            return [
                GridMessage(player),
                ChatMessage(StaticSender("SYSTEM"), current_map, "Game has been reset with fresh map state!")
            ]

        return [ChatMessage(StaticSender("SYSTEM"), current_map, "Could not reset this map!")]